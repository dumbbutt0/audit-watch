#!/usr/bin/env python3
"""
defi_accounting_audit.py — DeFi debt/credit CONSERVATION detector + cross-function conservation-invariant
generator for accounting-heavy protocols (Zaros-class).

Two layers (read-time over the frozen coverage manifest, snippet-aware; NOT a gate, never mutates anything):
  1. Per-item accounting tagger — classifies each in-scope function via defi_accounting_taxonomy.classify(),
     with coverage status from coverage_dispositions.json (finding / examined-but-cleared / uncovered).
  2. Cross-function CONSERVATION INVARIANTS — the recall layer single-item lenses miss. For each seed
     invariant in config (debt_credit conservation across recalc→distribute→settle→rebalance, etc.) it
     resolves the participating functions against the manifest and reports which exist and their coverage,
     turning "these N functions jointly must conserve X" into a concrete review packet.

Addresses the Zaros Part 2 eval miss cluster (14/16 Highs): settleVaultsDebt, withdrawUsdTokenFromMarket,
getRealizedDebtUsd, recalculateVaultsCreditCapacity, rebalanceVaultsAssets, AutoDeleverageFactor, WETH reward
distribution, market-vault disconnection, usdcAvailableForEngine lockup.

Usage: python scripts/defi_accounting_audit.py [--manifest <path>] [--no-source]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import defi_accounting_taxonomy as acct  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}


# The coverage manifest's source_span sometimes clips a function to its comment+signature (the body's
# arithmetic lands a few lines past end_line). A conservation lens MUST see the body, so we extend the
# window by a lookahead margin. Over-reading a few neighbouring lines is safe here: the two-signal gate in
# the classifier (domain + transition/arith) controls false positives, and this is an advisory recall lens.
_SNIPPET_LOOKAHEAD = 25


def _snippet(file_rel, start, end, use_source):
    if not use_source or not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    if not lines:
        return ""
    lo = max(0, (start or 1) - 1)
    hi = min(len(lines), (end or start or 1) + _SNIPPET_LOOKAHEAD)
    return "\n".join(lines[lo:hi])[:6000]


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[defi_accounting_audit] no manifest items at {man_path}")
    tax = acct.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source

    def _cov(mid):
        st = disp.get(mid, {}).get("status")
        return ("covered_by_finding" if st == "finding" else "examined_but_cleared" if st == "cleared"
                else "deferred" if st == "deferred_out_of_scope" else "uncovered")

    detected = []
    # name -> list of detected entries (for invariant participant resolution)
    by_name: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        cls = acct.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                            it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("defi_accounting_sensitive"):
            continue
        entry = {
            "manifest_id": it["id"], "name": it.get("name"), "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"),
            "category": cls["category"], "accounting_domains": cls["accounting_domains"],
            "risk_tags": cls["risk_tags"], "high_risk": acct.is_high_risk(cls, tax),
            "severity_ceiling_hint": cls.get("severity_ceiling_hint"), "matched_on": cls.get("matched_on"),
            "signed_unsigned": cls.get("_signed_unsigned"), "oracle_scaled": cls.get("_oracle_scaled"),
            "read_only": cls.get("_read_only"),
            "coverage": _cov(it["id"]), "disposition_status": disp.get(it["id"], {}).get("status"),
            "clear_reason": (disp.get(it["id"], {}).get("clear_reason") or "")[:180]
            if disp.get(it["id"], {}).get("status") == "cleared" else "",
        }
        detected.append(entry)
        if it.get("name"):
            by_name[_norm(it.get("name"))].append(entry)

    # ── cross-function conservation invariants: resolve participants against the manifest ──
    invariants_out = []
    for inv in tax.get("cross_function_invariants", []):
        parts = []
        for fn in inv.get("participating_functions", []):
            fn_key = _norm(re.split(r"[ (]", fn)[0])  # strip "(writers)" etc.
            matches = by_name.get(fn_key, [])
            if matches:
                for m in matches:
                    parts.append({"function": m["name"], "contract": m["contract"],
                                  "coverage": m["coverage"], "high_risk": m["high_risk"],
                                  "manifest_id": m["manifest_id"]})
            else:
                parts.append({"function": fn, "contract": None, "coverage": "not_in_manifest",
                              "high_risk": False, "manifest_id": None})
        present = [p for p in parts if p["coverage"] != "not_in_manifest"]
        cleared = [p for p in parts if p["coverage"] in ("examined_but_cleared", "uncovered")]
        invariants_out.append({
            "invariant_id": inv["invariant_id"], "state_domains": inv.get("state_domains", []),
            "expected_conservation": inv.get("expected_conservation", ""),
            "risk_if_broken": inv.get("risk_if_broken", ""),
            "related_answer_key_miss_class": inv.get("related_answer_key_miss_class", ""),
            "suggested_specialist": inv.get("suggested_specialist", "logic"),
            "participants": parts, "participants_present": len(present),
            "participants_total": len(parts),
            "needs_review": bool(present) and bool(cleared),
            "review_prompt": (f"[{inv['invariant_id']}] Verify conservation: {inv.get('expected_conservation','')}. "
                              f"Participating functions present in scope: "
                              f"{', '.join(sorted({p['function'] for p in present})) or 'none'}. "
                              f"Use prompts/defi_accounting_review.md. Risk if broken: {inv.get('risk_if_broken','')}."),
        })

    by_cat = Counter(x["category"] for x in detected)
    by_domain = Counter(d for x in detected for d in x["accounting_domains"])
    high_risk = [x for x in detected if x["high_risk"]]
    cleared_high_risk = [x for x in detected if x["high_risk"] and x["coverage"] == "examined_but_cleared"]
    finding_linked = [x for x in detected if x["coverage"] == "covered_by_finding"]
    uncovered = [x for x in detected if x["coverage"] == "uncovered"]
    rereview = [x for x in detected if x["high_risk"] and x["coverage"] != "covered_by_finding"]

    # review packets grouped by category+contract (mirrors griefing lens)
    packets = []
    groups = defaultdict(list)
    for x in rereview:
        groups[(x["category"], x["contract"] or "?")].append(x)
    for (cat, contract), xs in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        meta = tax.get("categories", {}).get(cat, {})
        packets.append({"packet_id": f"ACCT-{cat}-{contract}", "label": "defi_accounting", "category": cat,
                        "contract": contract, "suggested_specialist": "logic",
                        "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
                        "item_ids": sorted(x["manifest_id"] for x in xs), "files": sorted({x["file"] for x in xs}),
                        "review_prompt": (f"Re-review {len(xs)} {cat} item(s) in {contract} under the DeFi "
                                          f"accounting-conservation lens (prompts/defi_accounting_review.md). "
                                          + (meta.get("review_hint") or ""))})

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": ts, "manifest": str(man_path), "is_gate": False, "source_snippets": use_source,
        "total_defi_accounting_sensitive": len(detected),
        "by_category": dict(by_cat.most_common()),
        "by_accounting_domain": dict(by_domain.most_common()),
        "high_risk_count": len(high_risk),
        "cross_function_invariants": invariants_out,
        "previously_cleared_high_risk": cleared_high_risk,
        "finding_linked": [x["manifest_id"] for x in finding_linked],
        "examined_but_cleared": [x["manifest_id"] for x in detected if x["coverage"] == "examined_but_cleared"],
        "uncovered": uncovered,
        "re_review_candidates": len(rereview), "recommended_review_packets": packets,
        "detected": detected,
    }
    out = audit_path("output") / "defi_accounting_audit.json"
    out.write_text(json.dumps(report, indent=2))

    # ── markdown: conservation invariants FIRST (the top section the spec asks for) ──
    md = [f"# DeFi debt/credit conservation audit\n",
          f"_Generated {ts} · manifest `{man_path}` · NOT a gate · advisory recall lens_\n",
          f"**{len(detected)}** accounting-sensitive · **{len(high_risk)}** high-risk · "
          f"**{len(rereview)}** re-review · **{len(invariants_out)}** conservation invariants\n",
          "## Cross-function debt / credit conservation invariants needing review",
          "_Each invariant spans multiple functions that look locally fine but must jointly conserve a quantity._\n",
          "| id | conservation property | present | needs review | specialist |",
          "|---|---|---|---|---|"]
    for inv in invariants_out:
        md.append(f"| {inv['invariant_id']} | {inv['expected_conservation'][:80]} | "
                  f"{inv['participants_present']}/{inv['participants_total']} | "
                  f"{'YES' if inv['needs_review'] else 'no'} | {inv['suggested_specialist']} |")
    md += ["\n### Invariant participants (resolved against manifest)\n"]
    for inv in invariants_out:
        present = [p for p in inv["participants"] if p["coverage"] != "not_in_manifest"]
        md.append(f"- **{inv['invariant_id']}** ({', '.join(inv['state_domains'])}) — {inv['expected_conservation']}")
        md.append(f"  - risk: {inv['risk_if_broken']}")
        md.append(f"  - participants: " + ", ".join(
            f"{p['function']}[{p['coverage'][:4]}]" for p in inv["participants"]) )
    md += ["\n## Previously cleared but high-risk accounting items\n",
           "| name | contract | category | domains | clear_reason |", "|---|---|---|---|---|"]
    for x in cleared_high_risk:
        md.append(f"| {x['name']} | {x['contract']} | {x['category']} | {','.join(x['accounting_domains'])} | {x['clear_reason']} |")
    md += ["\n## By category", "| category | n |", "|---|---|"] + [f"| {c} | {n} |" for c, n in by_cat.most_common()]
    md += ["\n## By accounting domain", "| domain | n |", "|---|---|"] + [f"| {d} | {n} |" for d, n in by_domain.most_common()]
    md += ["\n## Recommended review packets\n"] + [
        f"- **{p['packet_id']}** ({len(p['item_ids'])} items, sev≤{p['severity_ceiling_hint']}) → {p['suggested_specialist']}"
        for p in packets]
    (audit_path("output") / "defi_accounting_audit.md").write_text("\n".join(md))

    print(f"[ok] defi_accounting_audit → {out}")
    print(f"     detected {len(detected)} · high-risk {len(high_risk)} · re-review {len(rereview)} "
          f"· invariants {len(invariants_out)}")
    print(f"     by_category {dict(by_cat.most_common())}")
    print(f"     by_accounting_domain {dict(by_domain.most_common())}")
    print(f"     previously-cleared high-risk ({len(cleared_high_risk)}): "
          f"{[(x['name'], x['category']) for x in cleared_high_risk][:12]}")
    inv_review = [i['invariant_id'] for i in invariants_out if i['needs_review']]
    print(f"     invariants needing review: {inv_review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
