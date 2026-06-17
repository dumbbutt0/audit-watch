#!/usr/bin/env python3
"""
silo_stalk_audit.py — Silo stalk/stem conservation detector + review-packet report.

Applies the silo_stalk_patterns.json taxonomy (via silo_stalk_taxonomy.classify) to the coverage manifest.
The signal lives in function BODIES, so this detector READS THE SOURCE SNIPPET around each manifest
source_span and classifies on it. It also resolves the config's cross-function CONSERVATION INVARIANTS
against the manifest (migration-flow style). Cross-references dispositions (finding / cleared / deferred).
Read-time over the (frozen) manifest — no rebuild — so eval3 integrity is preserved. Pure report; NOT a gate.

Headline: "Silo stalk/stem conservation invariants needing review" — a Silo bookkeeping helper cleared as
"conserves totals / pure helper" can still hide a rounding-direction, stem-legitimacy, or unit-scale bug.

Reads:  output/coverage_manifest.json (or --manifest), config/silo_stalk_patterns.json,
        output/coverage_dispositions.json (optional), + source files for snippets.
Writes: output/silo_stalk_audit.{json,md}

Usage: python scripts/silo_stalk_audit.py [--manifest <path>] [--no-source]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import silo_stalk_taxonomy as silo  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Honest mapping of category -> residual eval miss it plausibly recovers (all three are finding-linked in
# the frozen dispositions; the lens re-surfaces them as conservation review obligations).
CATEGORY_TO_MISS = {
    "rounding_direction": ["#241 transferStalk roundUp roots rounding"],
    "roots_stalk_ratio": ["#241 roots/stalk ratio on stalk transfer"],
    "stalk_transfer": ["#241 LibSilo.transferStalk conservation"],
    "user_vs_global_stalk": ["#241-adjacent user/global stalk sync"],
    "deposit_stem_mismatch": ["#364 transferDeposit caller-supplied stem"],
    "deposit_transfer": ["#364 transferDeposit preserves amount/BDV/stem"],
    "deposit_batch_transfer": ["#364 transferDeposits batch stem integrity"],
    "partial_deposit_transfer": ["#364 partial transfer stem manipulation"],
    "grown_stalk": ["#364 grown-stalk inflation via stem"],
    "reward_scaling": ["#229 stalkReward missing stem-scale factor"],
    "stem_scale": ["#229 stem<->stalk scale (1e6) factor"],
    "silo_reward_conservation": ["#229 reward distribution scaling"],
}

_FILE_CACHE: dict[str, list[str]] = {}


def _snippet(file_rel: str, start: int, end: int, use_source: bool) -> str:
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
    a = max(0, (start or 1) - 1)
    b = min(len(lines), (end or start or 1) + 8)   # lookahead to capture the body arithmetic
    return "\n".join(lines[a:b])[:4000]


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def _resolve_invariants(tax: dict, fn_index: dict) -> list:
    """Resolve config cross_function_invariants against the manifest by case-insensitive substring on name.
    Mirrors migration_flow: a per-function finding does NOT discharge a cross-function conservation
    obligation, so review_status=needs_review whenever >=1 participant resolves."""
    out = []
    for inv in tax.get("cross_function_invariants", []):
        participants = []
        for pat in inv.get("source_functions", []):
            pl = pat.lower()
            for it in fn_index.values():
                if pl in it["name"].lower():
                    participants.append({"name": it["name"], "contract": it["contract"],
                                         "file": it["file"], "coverage": it["coverage"]})
        # dedupe by (contract,name)
        seen = set(); uniq = []
        for p in participants:
            k = (p["contract"], p["name"])
            if k not in seen:
                seen.add(k); uniq.append(p)
        n = len(uniq)
        all_finding = bool(uniq) and all(p["coverage"] == "covered_by_finding" for p in uniq)
        out.append({
            "invariant_id": inv["invariant_id"], "title": inv["title"],
            "state_domains": inv.get("state_domains", []),
            "expected_conservation_property": inv.get("expected_property"),
            "risk_if_broken": inv.get("risk_if_broken"),
            "related_miss": inv.get("related_miss"),
            "suggested_specialist": inv.get("suggested_specialist"),
            "review_prompt": inv.get("review_prompt"),
            "source_functions": uniq,
            "participant_count": n,
            "participants_all_finding_linked": all_finding,
            "review_status": "needs_review" if n else "no_participants_found",
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="manifest path (default: live coverage_manifest.json)")
    ap.add_argument("--no-source", action="store_true", help="classify on signature only (no body snippet)")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[silo_stalk_audit] no manifest items at {man_path}")
    tax = silo.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source

    detected = []
    fn_index = {}
    for it in items:
        if it.get("kind") not in ("function", "initializer"):
            continue
        name = it.get("name", "")
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        cls = silo.classify(name, it.get("signature", ""), it.get("file", ""), it.get("contract", ""),
                            snippet=snip, mutability=it.get("mutability", ""), tags=it.get("tags"), taxonomy=tax)
        if not cls.get("silo_stalk_sensitive"):
            continue
        d = disp.get(it["id"], {})
        status = d.get("status")
        coverage = ("covered_by_finding" if status == "finding"
                    else "examined_but_cleared" if status == "cleared"
                    else "deferred" if status and status.startswith("deferred") else "uncovered")
        row = {
            "manifest_id": it["id"], "name": name, "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"), "mutability": it.get("mutability"),
            "category": cls["category"], "accounting_domains": cls["accounting_domains"],
            "risk_tags": cls["risk_tags"], "high_risk": silo.is_high_risk(cls, tax),
            "severity_ceiling_hint": cls["severity_ceiling_hint"], "in_scope": it.get("in_scope", True),
            "coverage": coverage, "disposition_status": status, "finding_refs": d.get("finding_refs", []),
            "clear_reason": d.get("clear_reason"), "signature": (it.get("signature") or "")[:200],
        }
        detected.append(row)
        fn_index[it["id"]] = {"name": name, "contract": it.get("contract"), "file": it.get("file"),
                              "coverage": coverage}

    # invariants resolve against ALL in-scope functions, not just detected ones
    full_fn_index = {}
    for it in items:
        if it.get("kind") not in ("function", "initializer") or not it.get("in_scope", True):
            continue
        d = disp.get(it["id"], {}); status = d.get("status")
        cov = ("covered_by_finding" if status == "finding"
               else "examined_but_cleared" if status == "cleared"
               else "deferred" if status and status.startswith("deferred") else "uncovered")
        full_fn_index[it["id"]] = {"name": it.get("name", ""), "contract": it.get("contract"),
                                   "file": it.get("file"), "coverage": cov}
    invariants = _resolve_invariants(tax, full_fn_index)

    by_category = Counter(x["category"] for x in detected)
    by_domain = Counter(d for x in detected for d in x["accounting_domains"])
    high_risk = [x for x in detected if x["high_risk"]]
    prev_cleared_hr = [x for x in detected if x["high_risk"] and x["coverage"] == "examined_but_cleared"]
    finding_linked = [x["manifest_id"] for x in detected if x["coverage"] == "covered_by_finding"]
    examined_cleared = [x["manifest_id"] for x in detected if x["coverage"] == "examined_but_cleared"]
    uncovered = [x["manifest_id"] for x in detected if x["coverage"] == "uncovered"]
    re_review = [x for x in detected if x["high_risk"] and x["coverage"] != "covered_by_finding"]

    by_cat_items = defaultdict(list)
    for x in re_review:
        by_cat_items[x["category"]].append(x)
    packets = []
    for i, (cat, xs) in enumerate(sorted(by_cat_items.items()), 1):
        meta = tax.get("categories", {}).get(cat, {})
        packets.append({
            "packet_id": f"SS-{i:02d}", "label": f"silo/stalk: {cat}", "category": cat,
            "suggested_specialist": "logic",
            "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
            "item_ids": sorted(x["manifest_id"] for x in xs),
            "files": sorted({x["file"] for x in xs if x["file"]}),
            "review_prompt": ("Reconcile this Silo accounting flow against conservation of amount/BDV/stem/"
                              "stalk/grown-stalk/roots (prompts/silo_stalk_review.md). " + (meta.get("review_hint") or "")),
        })

    likely = []
    for cat in by_category:
        likely += CATEGORY_TO_MISS.get(cat, [])
    likely = sorted(set(likely))

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": ts, "manifest": str(man_path), "is_gate": False, "source_snippets": use_source,
        "lens": "silo_stalk_conservation",
        "total_silo_stalk_sensitive": len(detected),
        "by_category": dict(by_category), "by_accounting_domain": dict(by_domain),
        "high_risk_count": len(high_risk), "re_review_candidates": len(re_review),
        "cross_function_invariants": invariants,
        "previously_cleared_high_risk": prev_cleared_hr,
        "covered_by_finding": finding_linked,
        "examined_but_cleared": examined_cleared,
        "uncovered": uncovered,
        "recommended_review_packets": packets,
        "likely_eval_miss_classes_recovered": likely,
        "detected": detected,
    }
    out = audit_path("output") / "silo_stalk_audit.json"
    out.write_text(json.dumps(report, indent=2))

    need = [i for i in invariants if i["review_status"] == "needs_review"]
    md = [f"# Silo stalk/stem conservation audit\n",
          f"_Generated {ts} · manifest `{man_path}` · source_snippets={use_source} · NOT a gate_\n",
          f"Total Silo/stalk-sensitive: **{len(detected)}** · high-risk **{len(high_risk)}** · "
          f"re-review **{len(re_review)}** · finding-linked **{len(finding_linked)}** · "
          f"cleared **{len(examined_cleared)}**\n",
          "## Silo stalk/stem conservation invariants needing review\n"]
    for inv in need:
        md.append(f"- **{inv['invariant_id']}** {inv['title']} "
                  f"(related {inv['related_miss'] or '-'}, {inv['participant_count']} participants"
                  f"{', all finding-linked' if inv['participants_all_finding_linked'] else ''}) — "
                  f"_{inv['expected_conservation_property']}_")
    md.append("\n## Previously cleared but high-risk Silo/stalk items\n")
    if prev_cleared_hr:
        for x in sorted(prev_cleared_hr, key=lambda r: (r["category"], r["contract"] or "")):
            md.append(f"- **{x['contract']}.{x['name']}** ({x['category']}, domains={x['accounting_domains']}) "
                      f"— `{x['file']}:{x['line']}` — cleared: _{(x['clear_reason'] or '')[:90]}_")
    else:
        md.append("- (none)")
    md.append("\n## Counts by category\n")
    for cat, n in by_category.most_common():
        md.append(f"- {cat}: {n}")
    md.append("\n## Counts by accounting domain\n")
    for dom, n in by_domain.most_common():
        md.append(f"- {dom}: {n}")
    md.append("\n## Recommended review packets\n")
    for p in packets:
        md.append(f"- **{p['packet_id']}** {p['label']} ({len(p['item_ids'])} items) — {p['files']}")
    md.append("\n## Likely residual miss classes recovered\n")
    for l in likely:
        md.append(f"- {l}")
    (audit_path("output") / "silo_stalk_audit.md").write_text("\n".join(md))
    print(f"[silo_stalk_audit] {len(detected)} sensitive · {len(high_risk)} high-risk · "
          f"{len(prev_cleared_hr)} previously-cleared-high-risk · {len(need)} invariants need review · wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
