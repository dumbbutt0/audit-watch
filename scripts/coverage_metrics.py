#!/usr/bin/env python3
"""
coverage_metrics.py — Decompose coverage from detection (deterministic, no LLM).

Writes output/coverage_metrics.json: how much of the denominator was examined (coverage), separate
from how many findings came out of it (detection). This is the metric that the 42% Beanstalk eval
conflated. Lets future evals report coverage% vs detection-on-covered vs missed-surface separately.

Usage:
    python scripts/coverage_metrics.py [--quiet]
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = audit_path("output") / "coverage_manifest.json"
    disp_path = audit_path("output") / "coverage_dispositions.json"
    if not man_path.exists() or not disp_path.exists():
        raise SystemExit("[coverage_metrics] manifest or dispositions missing — build them first.")

    items = {i["id"]: i for i in json.loads(man_path.read_text()).get("items", [])}
    disp = {d["manifest_id"]: d for d in json.loads(disp_path.read_text()).get("dispositions", [])}

    in_scope = {mid: m for mid, m in items.items() if m.get("in_scope", True)}
    status_of = {mid: disp.get(mid, {}).get("status", "unassigned") for mid in in_scope}
    pass_of = {mid: (disp.get(mid, {}) or {}).get("assigned_pass") for mid in in_scope}

    sc = Counter(status_of.values())
    n = len(in_scope) or 1
    examined_like = sc["examined"] + sc["cleared"] + sc["finding"]
    resolved = sc["cleared"] + sc["finding"]

    # pass decomposition (deep vs cheap_sweep) over examined-like items
    pass_counter = Counter(pass_of[mid] for mid in in_scope if status_of[mid] in ("examined", "cleared", "finding"))

    # tag breakdowns
    finding_by_tag: dict[str, int] = defaultdict(int)
    unexamined_by_tag: dict[str, int] = defaultdict(int)
    for mid, m in in_scope.items():
        st = status_of[mid]
        for t in m.get("tags", []):
            if st == "finding":
                finding_by_tag[t] += 1
            if st in ("unassigned", "assigned"):
                unexamined_by_tag[t] += 1

    unexamined_high = sorted(
        [{"id": mid, "score": m.get("attack_surface_score", 0), "kind": m["kind"],
          "file": m["file"], "name": m["name"], "tags": m.get("tags", [])}
         for mid, m in in_scope.items()
         if status_of[mid] in ("unassigned", "assigned")],
        key=lambda x: -x["score"])

    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_manifest_items": len(items),
        "in_scope_items": len(in_scope),
        "out_of_scope_items": len(items) - len(in_scope),
        "examined_items": examined_like,
        "cleared_items": sc["cleared"],
        "finding_linked_items": sc["finding"],
        "unassigned_items": sc["unassigned"],
        "assigned_only_items": sc["assigned"],
        "coverage_percent": round(100.0 * resolved / n, 1),
        "examined_percent": round(100.0 * examined_like / n, 1),
        "deep_pass_percent": round(100.0 * pass_counter.get("deep", 0) / n, 1),
        "cheap_sweep_percent": round(100.0 * pass_counter.get("cheap_sweep", 0) / n, 1),
        "finding_density_by_tag": dict(sorted(finding_by_tag.items(), key=lambda x: -x[1])),
        "unexamined_by_tag": dict(sorted(unexamined_by_tag.items(), key=lambda x: -x[1])),
        "unexamined_high_score_items": unexamined_high[:25],
        "top_coverage_gaps": [u["id"] for u in unexamined_high[:15]],
    }
    out = audit_path("output") / "coverage_metrics.json"
    out.write_text(json.dumps(metrics, indent=2))

    if not args.quiet:
        print(f"[ok] coverage metrics → {out}")
        print(f"     coverage {metrics['coverage_percent']}% (resolved {resolved}/{len(in_scope)} in-scope) · "
              f"examined {metrics['examined_percent']}%")
        print(f"     deep {metrics['deep_pass_percent']}% · cheap-sweep {metrics['cheap_sweep_percent']}% · "
              f"unassigned {sc['unassigned']}")
        if unexamined_high:
            print(f"     top unexamined high-score: {', '.join(u['id'] for u in unexamined_high[:5])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
