#!/usr/bin/env python3
"""
P178 measurement (READ-ONLY) — run the deterministic dependency-metadata extractor over the EXISTING clears of
zaros + revert-lend and report capture coverage, structured-vs-prose, and the routing preview under the
UNCHANGED P177 rule. Writes ONLY capture_coverage.json next to this file. No corpus mutation.

Run: python documentation/research/assisted_mode/p178_structured_dependency_capture/measure_capture.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import dependency_clear_utils as dcu          # noqa: E402
import dependency_metadata as dmeta           # noqa: E402

CORPORA = {"zaros": "zaros-2025-01-part-2-eval", "revert-lend": "revert-lend-2024-03-strict-eval"}


def measure(audit_id):
    disp = json.loads((ROOT / f"audits/{audit_id}/output/coverage_dispositions.json").read_text())["dispositions"]
    man = json.loads((ROOT / f"audits/{audit_id}/output/coverage_manifest.json").read_text())["items"]
    mi = {i["id"]: i for i in man}
    ni = dcu.build_manifest_name_index(man)
    di = {d["manifest_id"]: d for d in disp}
    cleared = [d for d in disp if d.get("status") == "cleared"]
    dep_based = [d for d in cleared if dcu.is_dependency_based_clear(d)]

    verdicts = Counter()
    routing = Counter()
    name = scope = status = proof = 0
    for d in dep_based:
        # run extractor on a COPY (read-only; never write back to the corpus)
        meta = dmeta.extract_dependency_metadata(dict(d), manifest_index=mi, name_index=ni, disposition_index=di)
        verdicts[dmeta.validate_dependency_metadata(meta)] += 1
        if meta.get("dependency_name"):
            name += 1
        if meta.get("dependency_scope") not in (None, "unknown"):
            scope += 1
        if meta.get("dependency_status") not in (None, "missing"):
            status += 1
        if meta.get("proof_status") not in (None, "not_applicable"):
            proof += 1
        # routing preview under the UNCHANGED P177 rule, on the extractor-enriched clear
        enriched = dict(d)
        enriched.update({k: v for k, v in meta.items() if v is not None})
        cls = dcu.classify_clear(enriched, di, ni, manifest_index=mi)
        routing[dcu.dependency_route_decision(cls, enriched, locality_on=True, require_structured=True)] += 1

    n = len(dep_based)
    pct = lambda k: round(100 * k / n, 1) if n else 0.0  # noqa: E731
    complete = verdicts.get("metadata_complete", 0)
    prose = verdicts.get("dependency_name_unresolved", 0) + verdicts.get("generic_dependency_name", 0)
    return {
        "cleared_total": len(cleared), "dependency_based_clears": n,
        "coverage_over_dependency_based": {"dependency_name_pct": pct(name), "dependency_scope_pct": pct(scope),
                                           "dependency_status_pct": pct(status), "proof_status_pct": pct(proof)},
        "verdicts": dict(verdicts),
        "structured_complete": complete, "prose_only_unresolved": prose,
        "structured_gt_prose": complete > prose,
        "routing_preview_after_capture": dict(routing),
    }


def main():
    out = {"phase": "P178", "type": "structured_dependency_capture_measurement", "read_only": True,
           "corpora": {c: measure(aid) for c, aid in CORPORA.items()}}
    (HERE / "capture_coverage.json").write_text(json.dumps(out, indent=2))
    for c, r in out["corpora"].items():
        print(f"\n===== {c} =====")
        print(f"dependency-based clears: {r['dependency_based_clears']} / {r['cleared_total']} cleared")
        print(f"coverage (over dep-based): {r['coverage_over_dependency_based']}")
        print(f"verdicts: {r['verdicts']}")
        print(f"structured_complete={r['structured_complete']}  prose_only_unresolved={r['prose_only_unresolved']}"
              f"  structured>prose={r['structured_gt_prose']}")
        print(f"routing preview after capture (P177 rule): {r['routing_preview_after_capture']}")
    print("\n[OK] read-only; wrote capture_coverage.json only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
