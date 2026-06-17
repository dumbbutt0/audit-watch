#!/usr/bin/env python3
"""
coverage_completeness_report.py — RESEARCH-ONLY, deterministic coverage-completeness reporter.

Answers "which in-scope files/functions were NOT read?" so a blind/reach run can never silently miss a bug because
code was never examined. Reads the EXISTING production artifacts READ-ONLY:
  audits/<target>/output/coverage_manifest.json   (every in-scope item, enumerated from source)
  audits/<target>/output/coverage_dispositions.json (per-item status)

Resolved = finding|cleared. Unexamined = unassigned|assigned|examined (still owed a terminal disposition).
Deferred = deferred_out_of_scope. coverage_percent = 100 * resolved / in_scope. complete iff unexamined == 0.

Emits the per-file unexamined table (the explicit gap list) + coverage_percent. Sets NO disposition, mints NO
finding, never blocks — it only REPORTS (the production coverage_completeness_gate is the blocking gate).

Usage: python scripts/research/coverage_completeness_report.py <target> [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESOLVED = {"finding", "cleared"}
UNEXAMINED = {"unassigned", "assigned", "examined"}
_STAMP = {"research_only": True, "is_gate": False, "emits_findings": False, "severity": None,
          "auto_submitted": False, "routes_in_production": False}


def _audit_out(target: str) -> Path:
    return ROOT / "audits" / target / "output"


def coverage_report(target: str) -> dict:
    """Pure: read manifest+dispositions, return the coverage-completeness report (no writes)."""
    out = _audit_out(target)
    manifest = json.loads((out / "coverage_manifest.json").read_text())
    disp = json.loads((out / "coverage_dispositions.json").read_text()).get("dispositions", [])
    disp_idx = {d.get("manifest_id"): d for d in disp}

    items = [m for m in manifest.get("items", []) if m.get("in_scope", True)]
    counts = {"finding": 0, "cleared": 0, "examined": 0, "assigned": 0, "unassigned": 0,
              "deferred_out_of_scope": 0, "no_disposition": 0}
    per_file: dict[str, dict] = defaultdict(lambda: {"unexamined": 0, "max_score": 0, "items": []})
    for m in items:
        d = disp_idx.get(m["id"])
        st = d.get("status") if d else "no_disposition"
        counts[st] = counts.get(st, 0) + 1
        if st in UNEXAMINED or st == "no_disposition":
            f = m.get("file", "?")
            pf = per_file[f]
            pf["unexamined"] += 1
            pf["max_score"] = max(pf["max_score"], m.get("attack_surface_score", 0))
            if len(pf["items"]) < 12:
                pf["items"].append({"name": m.get("name"), "kind": m.get("kind"),
                                    "score": m.get("attack_surface_score", 0), "status": st})

    in_scope = len(items)
    resolved = counts["finding"] + counts["cleared"]
    unexamined = counts["unassigned"] + counts["assigned"] + counts["examined"] + counts["no_disposition"]
    unexamined_files = sorted(
        ({"file": f.replace(str(ROOT) + "/", "").split("/contracts/")[-1], "unexamined": v["unexamined"],
          "max_score": v["max_score"], "items": v["items"]} for f, v in per_file.items()),
        key=lambda x: (-x["max_score"], -x["unexamined"], x["file"]))
    return dict(_STAMP, label="P309_COVERAGE_COMPLETENESS", target=target,
                in_scope=in_scope, resolved=resolved, unexamined=unexamined,
                deferred_out_of_scope=counts["deferred_out_of_scope"],
                coverage_percent=round(100.0 * resolved / in_scope, 1) if in_scope else 0.0,
                complete=(unexamined == 0), status_counts=counts,
                unexamined_file_count=len(unexamined_files), unexamined_files=unexamined_files)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rep = coverage_report(a.target)
    out_dir = ROOT / "documentation/research/assisted_mode/p302_blind_reach_test/outputs" / a.target
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "coverage_report.json").write_text(json.dumps(rep, indent=2))
    if a.json:
        print(json.dumps({k: rep[k] for k in ("target", "in_scope", "resolved", "unexamined",
              "coverage_percent", "complete", "unexamined_file_count")}, indent=2))
    else:
        print(f"COVERAGE {a.target}: {rep['coverage_percent']}%  ·  in-scope {rep['in_scope']} · resolved "
              f"{rep['resolved']} · UNEXAMINED {rep['unexamined']} across {rep['unexamined_file_count']} files "
              f"· complete={rep['complete']}")
        print("  Top unexamined files (NOT read/cleared — would silently miss bugs here):")
        for uf in rep["unexamined_files"][:20]:
            print(f"    [{uf['max_score']}] {uf['unexamined']:3d}  {uf['file']}")
        if rep["unexamined_file_count"] > 20:
            print(f"    … +{rep['unexamined_file_count']-20} more files (see coverage_report.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
