#!/usr/bin/env python3
"""
migration_flow_audit.py — Migration-flow state-model detector + cross-function invariant graph.

Two layers:
  (1) per-item migration tagger (read-time over the frozen manifest, snippet-aware) — like the prior lenses;
  (2) the NOVEL layer: resolves the curated `cross_function_invariants` against the manifest — for each
      invariant it finds the participating in-scope functions, attaches their dispositions, and reports a
      conservation property + risk + the answer-key miss it maps to. This is the first CROSS-FUNCTION model:
      it surfaces flows that are locally correct but globally break migrated state (#242/#248/#451/#452/#462).

Reads manifest + dispositions + config/migration_flow_patterns.json (+ source snippets). NOT a gate; never
mutates eval3 artifacts. Writes output/migration_flow_audit.{json,md}.

Usage: python scripts/migration_flow_audit.py [--manifest <path>] [--no-source]
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
import migration_flow_taxonomy as mig  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CATEGORY_TO_MISS = {
    "grown_stalk_recompute": ["#242 addMigratedDepositsToAccount forfeits unmowed rewards"],
    "deposit_array_migration": ["#248 migrated deposit not pushed to depositId list"],
    "claimable_balance_migration": ["#451 orderers lose Beans after migration"],
    "plenty_migration": ["#451 plenty/claimable not migrated"],
    "stalk_migration": ["#452 migrated users receive less stalk"],
    "sum_of_users_vs_global": ["#452 sum-of-users != global stalk"],
    "global_total_migration": ["#452 global totals desynced"],
    "one_shot_guard": ["#462 replayable/partial migration"],
    "l2_receiver": ["#462 stuck tokens / receiver validation"],
}
_FILE_CACHE: dict[str, list[str]] = {}


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
    return "\n".join(lines[max(0, (start or 1) - 1):min(len(lines), end or start or 1)])[:4000]


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[migration_flow_audit] no manifest items at {man_path}")
    tax = mig.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source

    def _cov(mid):
        st = disp.get(mid, {}).get("status")
        return ("covered_by_finding" if st == "finding" else "examined_but_cleared" if st == "cleared"
                else "deferred" if st == "deferred_out_of_scope" else "uncovered")

    detected, fn_index = [], []  # fn_index: in-scope functions (for invariant resolution)
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        fn_index.append(it)
        cls = mig.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                          it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("migration_flow_sensitive"):
            continue
        detected.append({
            "manifest_id": it["id"], "name": it.get("name"), "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"),
            "category": cls["category"], "risk_tags": cls["risk_tags"], "state_domains": cls["state_domains"],
            "high_risk": mig.is_high_risk(cls, tax), "severity_ceiling_hint": cls.get("severity_ceiling_hint"),
            "matched_on": cls.get("matched_on"), "coverage": _cov(it["id"]),
            "disposition_status": disp.get(it["id"], {}).get("status"),
            "clear_reason": (disp.get(it["id"], {}).get("clear_reason") or "")[:160]
            if disp.get(it["id"], {}).get("status") == "cleared" else "",
        })

    # ── cross-function invariant resolution ──
    invariants = []
    for inv in tax.get("cross_function_invariants", []):
        pats = [p.lower() for p in inv.get("function_name_patterns", [])]
        parts = []
        seen = set()
        for it in fn_index:
            nl = (it.get("name") or "").lower()
            if any(p in nl for p in pats):
                # participants must be in a migration context (a reseed/L1/L2 file or migration-named) —
                # otherwise a bare 'init'/'total' pattern would pull every initializer/getter in the repo.
                if not mig.has_migration_context(it.get("name", ""), it.get("file", ""),
                                                 signature=it.get("signature", ""), taxonomy=tax):
                    continue
                key = (it.get("name"), it.get("contract"))
                if key in seen:
                    continue
                seen.add(key)
                parts.append({"name": it.get("name"), "contract": it.get("contract"),
                              "file": it.get("file"), "coverage": _cov(it["id"])})
        covs = {p["coverage"] for p in parts}
        # A cross-function conservation invariant is a DISTINCT review obligation: per-function findings on
        # the participants do NOT discharge it (the whole point — these functions are findings for OTHER
        # aspects while the conservation property went unchecked; that is why #242/#248/#451/#452 were
        # missed). So: needs_review whenever participants exist; no_participants_found otherwise. Whether
        # the participants are already finding-linked is reported separately as context.
        review_status = "no_participants_found" if not parts else "needs_review"
        invariants.append({**{k: inv[k] for k in ("invariant_id", "title", "state_domains",
                                                  "expected_conservation_property", "risk_if_broken", "related_miss")},
                           "source_functions": parts, "participant_count": len(parts),
                           "participants_all_finding_linked": bool(parts) and covs == {"covered_by_finding"},
                           "review_status": review_status})

    by_cat = Counter(x["category"] for x in detected)
    by_domain = Counter(d for x in detected for d in x["state_domains"])
    high_risk = [x for x in detected if x["high_risk"]]
    cleared_high_risk = [x for x in detected if x["high_risk"] and x["coverage"] == "examined_but_cleared"]
    rereview = [x for x in detected if x["high_risk"] and x["coverage"] != "covered_by_finding"]

    packets = []
    groups = defaultdict(list)
    for x in rereview:
        groups[(x["category"], x["contract"] or "?")].append(x)
    for (cat, contract), xs in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        meta = tax.get("categories", {}).get(cat, {})
        packets.append({"packet_id": f"MIG-{cat}-{contract}", "label": "migration_flow", "category": cat,
                        "contract": contract, "suggested_specialist": "logic",
                        "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
                        "item_ids": sorted(x["manifest_id"] for x in xs), "files": sorted({x["file"] for x in xs}),
                        "review_prompt": (f"Re-review {len(xs)} {cat} item(s) in {contract} under the migration-flow "
                                          f"lens (prompts/migration_flow_review.md). " + (meta.get("review_hint") or ""))})

    miss_classes = sorted({m for x in detected for m in CATEGORY_TO_MISS.get(x["category"], [])}
                          | {inv["related_miss"] for inv in invariants if inv.get("related_miss")})

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "generated_at": ts, "manifest": str(man_path), "is_gate": False, "source_snippets": use_source,
        "total_migration_flow_sensitive": len(detected), "by_category": dict(by_cat.most_common()),
        "by_state_domain": dict(by_domain.most_common()), "high_risk_count": len(high_risk),
        "cross_function_invariants": invariants,
        "previously_cleared_high_risk": cleared_high_risk,
        "covered_by_finding": [x["manifest_id"] for x in detected if x["coverage"] == "covered_by_finding"],
        "examined_but_cleared": [x["manifest_id"] for x in detected if x["coverage"] == "examined_but_cleared"],
        "uncovered": [x for x in detected if x["coverage"] == "uncovered"],
        "re_review_candidates": len(rereview), "recommended_review_packets": packets,
        "likely_eval_miss_classes_recovered": miss_classes, "detected": detected,
    }
    out = audit_path("output") / "migration_flow_audit.json"
    out.write_text(json.dumps(report, indent=2))

    needs = [i for i in invariants if i["review_status"] == "needs_review"]
    md = [f"# Migration-flow state-model audit\n", f"_Generated {ts} · manifest `{man_path}` · NOT a gate_\n",
          f"**{len(detected)}** migration-flow-sensitive · **{len(high_risk)}** high-risk · "
          f"**{len(invariants)}** cross-function invariants ({len(needs)} need review)\n",
          "## ⛓ Cross-function migration invariants needing review",
          "_Locally-correct functions can still break global migrated state. Each invariant links the "
          "participating functions + their dispositions._\n",
          "| invariant | miss | status | state domains | participants (disposition) |", "|---|---|---|---|---|"]
    for i in invariants:
        parts = ", ".join(f"{p['name']}[{p['coverage'][:4]}]" for p in i["source_functions"][:6]) or "—"
        md.append(f"| {i['invariant_id']} {i['title']} | {i['related_miss'] or ''} | {i['review_status']} "
                  f"| {', '.join(i['state_domains'])} | {parts} |")
    md += ["\n### Invariant detail\n"]
    for i in needs:
        md += [f"**{i['invariant_id']} — {i['title']}** ({i['related_miss'] or 'no mapped miss'})",
               f"- property: {i['expected_conservation_property']}", f"- risk: {i['risk_if_broken']}",
               f"- participants: " + (", ".join(f"{p['name']} ({p['contract']}) [{p['coverage']}]"
                                                 for p in i["source_functions"]) or "none"), ""]
    md += ["## ⚠ Previously cleared but high-risk migration items\n",
           "| name | contract | category | clear_reason |", "|---|---|---|---|"]
    for x in cleared_high_risk:
        md.append(f"| {x['name']} | {x['contract']} | {x['category']} | {x['clear_reason']} |")
    md += ["\n## By category", "| category | n |", "|---|---|"] + [f"| {c} | {n} |" for c, n in by_cat.most_common()]
    md += ["\n## By state domain", "| domain | n |", "|---|---|"] + [f"| {d} | {n} |" for d, n in by_domain.most_common()]
    md += ["\n## Recommended review packets\n"] + [
        f"- **{p['packet_id']}** ({len(p['item_ids'])} items, sev≤{p['severity_ceiling_hint']}) → {p['suggested_specialist']}"
        for p in packets]
    md += ["\n## Likely eval miss classes this lens addresses\n"] + [f"- {m}" for m in miss_classes]
    (audit_path("output") / "migration_flow_audit.md").write_text("\n".join(md))

    print(f"[ok] migration_flow_audit → {out}")
    print(f"     detected {len(detected)} · high-risk {len(high_risk)} · re-review {len(rereview)}")
    print(f"     invariants {len(invariants)} ({len(needs)} need review) · by_domain {dict(by_domain.most_common())}")
    print(f"     by_category {dict(by_cat.most_common())}")
    for i in needs:
        if i["related_miss"]:
            print(f"     {i['invariant_id']} {i['related_miss']}: {i['participant_count']} participants ({i['review_status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
