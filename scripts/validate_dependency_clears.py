#!/usr/bin/env python3
"""
validate_dependency_clears.py — flag coverage clears that lean on an unreviewed downstream dependency.

Reads output/coverage_manifest.json + output/coverage_dispositions.json (read-only on both). For every
`cleared` disposition it classifies whether the clear is dependency-based and, if so, whether the
dependency it relies on has itself been reviewed (finding-linked / cleared-with-evidence / out-of-scope).

A dependency is not a proof unless the dependency itself was reviewed. See
documentation/dependency_clear_policy.md. This validator NEVER mutates dispositions — it only writes
output/dependency_clear_validation.{json,md}.

Statuses per item: not_dependency_based | dependency_valid | finding_linked_dependency |
                   missing_dependency_metadata | unreviewed_dependency | unknown_dependency |
                   dependency_evidence_missing
(finding_linked_dependency is non-blocking: the clear cites an existing finding, so the dependency has
already been reviewed/filed.)

Modes:
  --mode advisory  (default) exit 0; report all suspicious clears
  --mode strict    exit nonzero if any blocking dependency-clear exists

Usage:
  python scripts/validate_dependency_clears.py --mode advisory
  python scripts/validate_dependency_clears.py --mode strict
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import dependency_clear_utils as dcu  # noqa: E402

# rule-math / estimator / guard signal tokens for the QuantAMM-style report breakdown
RISKY_TOKENS = ["_guardquantammweights", "mathguard", "covariance", "variance", "gradient",
                "estimator", "interpolation", "staleness", "guard rail", "guardrail", "epsilon"]


def _involves_risky(disp: dict) -> bool:
    blob = " ".join(str(disp.get(k) or "") for k in
                    ("clear_reason", "guard_or_invariant", "no_impact_reason", "dependency_reason")).lower()
    blob += " " + " ".join(str(x) for x in (disp.get("clear_depends_on") or [])).lower()
    return any(t in blob for t in RISKY_TOKENS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["advisory", "strict"], default="advisory")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = audit_path("output") / "coverage_manifest.json"
    disp_path = audit_path("output") / "coverage_dispositions.json"
    if not disp_path.exists():
        raise SystemExit("[validate_dependency_clears] coverage_dispositions.json missing — run the coverage pipeline first.")

    manifest_items = []
    if man_path.exists():
        try:
            manifest_items = json.loads(man_path.read_text()).get("items", [])
        except (json.JSONDecodeError, OSError):
            manifest_items = []
    name_index = dcu.build_manifest_name_index(manifest_items)
    manifest_index = {i["id"]: i for i in manifest_items}
    score_of = {i["id"]: i.get("attack_surface_score", 0) for i in manifest_items}

    # locality / path-dominance is gated by its own config flag so it can be tuned independently.
    try:
        pol = json.loads((Path(__file__).resolve().parent.parent / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except (OSError, json.JSONDecodeError):
        pol = {}
    full_audit = os.environ.get("AUDITWATCH_FULL_AUDIT", "").strip().lower() in ("1", "true", "yes", "on")
    locality_on = pol.get("dependency_locality_strict", False) or \
        (pol.get("dependency_locality_strict_full_audit", True) and full_audit)
    cg_path = audit_path("data") / "interactions" / "call_graph.json"
    call_graph = {}
    if cg_path.exists():
        try:
            call_graph = json.loads(cg_path.read_text())
        except (json.JSONDecodeError, OSError):
            call_graph = {}

    dispositions = json.loads(disp_path.read_text()).get("dispositions", [])
    disp_index = {d["manifest_id"]: d for d in dispositions}
    # P177: hard-blocking now requires complete structured metadata resolving an in-scope unproven guard
    # (reversible via guarded_downstream_require_structured); prose-only/incomplete → advisory.
    require_structured = pol.get("guarded_downstream_require_structured", True)
    blocking_statuses = ((dcu.STRUCTURED_BLOCKING if require_structured else dcu.BLOCKING_CLASSIFICATIONS)
                         | (dcu.LOCALITY_BLOCKING if locality_on else set()))

    rows = []
    for d in dispositions:
        if d.get("status") != "cleared":
            continue
        cls = dcu.classify_clear(d, disp_index, name_index, manifest_index=manifest_index, call_graph=call_graph)
        rows.append({
            "manifest_id": d["manifest_id"],
            "attack_surface_score": score_of.get(d["manifest_id"], 0),
            "status": cls["status"],
            "dependency_based": cls["dependency_based"],
            "dependency_names": cls["names"],
            "dependency_clearance_status": cls["clearance_status"],
            "computed_clearance": cls.get("computed_clearance"),
            "missing_metadata": cls["missing_metadata"],
            "guard_type": cls["guard_type"],
            "locality_reason": cls.get("locality_reason"),
            "involves_rule_math_or_guard": _involves_risky(d),
            "clear_reason": (d.get("clear_reason") or "")[:240],
        })

    counts = Counter(r["status"] for r in rows)
    dep_based = [r for r in rows if r["dependency_based"]]
    blocking = [r for r in rows if r["status"] in blocking_statuses]
    risky = [r for r in dep_based if r["involves_rule_math_or_guard"]]

    out = {
        "mode": args.mode,
        "locality_enforced": locality_on,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_cleared": len(rows),
        "dependency_based_clears": len(dep_based),
        "blocking": len(blocking),
        "by_status": dict(counts),
        "rule_math_or_guard_dependency_clears": len(risky),
        "rows": rows,
    }
    (audit_path("output") / "dependency_clear_validation.json").write_text(json.dumps(out, indent=2))

    md = ["# Dependency-clear validation", "",
          f"- mode: **{args.mode}**",
          f"- cleared dispositions: {len(rows)}",
          f"- dependency-based clears: **{len(dep_based)}**",
          f"- blocking (missing/unreviewed/unknown/evidence-missing): **{len(blocking)}**",
          f"- of which involve rule-math / estimator / guard: **{len(risky)}**", "",
          "## By classification", "", "| status | count |", "|---|---|"]
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        md.append(f"| {k} | {v} |")
    md += ["", "## Blocking dependency-based clears", "",
           "| manifest_id | score | status | clearance | guard_type | deps | reason |",
           "|---|---|---|---|---|---|---|"]
    for r in sorted(blocking, key=lambda r: -r["attack_surface_score"]):
        reason = r.get("locality_reason") or r["clear_reason"]
        md.append(f"| {r['manifest_id']} | {r['attack_surface_score']} | {r['status']} | "
                  f"{r['dependency_clearance_status']} | {r['guard_type']} | "
                  f"{', '.join(r['dependency_names'][:4])} | {reason[:90]} |")
    (audit_path("output") / "dependency_clear_validation.md").write_text("\n".join(md) + "\n")

    if not args.quiet:
        print(f"[dependency-clears] mode={args.mode} · cleared={len(rows)} · dependency-based={len(dep_based)} "
              f"· blocking={len(blocking)} · rule-math/guard={len(risky)}")
        print(f"  by_status: {dict(counts)}")
        for r in blocking[:12]:
            print(f"   BLOCK {r['manifest_id']} [{r['status']}] deps={r['dependency_names'][:3]}")

    if args.mode == "strict" and blocking:
        print(f"[FAIL] strict mode: {len(blocking)} dependency-based clear(s) rely on unreviewed/"
              f"undocumented dependencies. See output/dependency_clear_validation.md.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
