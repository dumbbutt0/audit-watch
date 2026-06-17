#!/usr/bin/env python3
"""
validate_dependency_metadata.py — P178 READ-ONLY report on structured dependency evidence capture.

For every dependency-based cleared disposition, runs the deterministic extractor and reports the capture
verdict (metadata_complete | metadata_incomplete | dependency_name_unresolved | generic_dependency_name) plus
coverage of the canonical fields. Writes output/dependency_metadata_validation.{json,md}. Never mutates
dispositions, never blocks (advisory).

Usage: python scripts/validate_dependency_metadata.py [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import dependency_clear_utils as dcu  # noqa: E402
import dependency_metadata as dmeta  # noqa: E402


def analyze(dispositions: list[dict], manifest_items: list[dict]) -> dict:
    man_idx = {i["id"]: i for i in manifest_items}
    name_index = dcu.build_manifest_name_index(manifest_items)
    disp_index = {d["manifest_id"]: d for d in dispositions}
    cleared = [d for d in dispositions if d.get("status") == "cleared"]
    dep_based = [d for d in cleared if dcu.is_dependency_based_clear(d)]

    verdicts = Counter()
    name_cov = scope_cov = status_cov = proof_cov = 0
    rows = []
    for d in dep_based:
        meta = dmeta.extract_dependency_metadata(d, manifest_index=man_idx, name_index=name_index,
                                                 disposition_index=disp_index)
        v = dmeta.validate_dependency_metadata(meta)
        verdicts[v] += 1
        if meta.get("dependency_name"):
            name_cov += 1
        if meta.get("dependency_scope") not in (None, "unknown"):
            scope_cov += 1
        if meta.get("dependency_status") not in (None, "missing"):
            status_cov += 1
        if meta.get("proof_status") not in (None, "not_applicable"):
            proof_cov += 1
        rows.append({"manifest_id": d["manifest_id"], "verdict": v,
                     "dependency_name": meta.get("dependency_name"),
                     "dependency_scope": meta.get("dependency_scope"),
                     "dependency_status": meta.get("dependency_status"),
                     "proof_status": meta.get("proof_status")})

    n = len(dep_based)
    pct = lambda k: round(100 * k / n, 1) if n else 0.0  # noqa: E731
    return {
        "cleared_total": len(cleared),
        "dependency_based_clears": n,
        "verdicts": dict(verdicts),
        "coverage_over_dependency_based": {
            "dependency_name_pct": pct(name_cov), "dependency_scope_pct": pct(scope_cov),
            "dependency_status_pct": pct(status_cov), "proof_status_pct": pct(proof_cov),
        },
        "structured_complete": verdicts.get("metadata_complete", 0),
        "prose_only_unresolved": verdicts.get("dependency_name_unresolved", 0)
        + verdicts.get("generic_dependency_name", 0),
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    disp_path = audit_path("output") / "coverage_dispositions.json"
    man_path = audit_path("output") / "coverage_manifest.json"
    if not disp_path.exists():
        raise SystemExit("[validate_dependency_metadata] coverage_dispositions.json missing.")
    dispositions = json.loads(disp_path.read_text()).get("dispositions", [])
    manifest_items = json.loads(man_path.read_text()).get("items", []) if man_path.exists() else []

    out = analyze(dispositions, manifest_items)
    (audit_path("output") / "dependency_metadata_validation.json").write_text(json.dumps(out, indent=2))
    md = [f"# Dependency metadata capture (P178) — advisory",
          f"- dependency-based clears: {out['dependency_based_clears']} / {out['cleared_total']} cleared",
          f"- verdicts: {out['verdicts']}",
          f"- coverage: {out['coverage_over_dependency_based']}",
          f"- structured_complete: {out['structured_complete']}  prose_only_unresolved: {out['prose_only_unresolved']}"]
    (audit_path("output") / "dependency_metadata_validation.md").write_text("\n".join(md) + "\n")
    if not args.quiet:
        print("\n".join(md))
    return 0  # advisory: never non-zero


if __name__ == "__main__":
    raise SystemExit(main())
