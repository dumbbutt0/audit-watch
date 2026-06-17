#!/usr/bin/env python3
"""
ingest_ground_truth.py — Record a human-verified finding outcome as ground truth.

This is the ONLY write path to data/evaluation/ground_truth.jsonl.
AI components may read but never write to this file — it is the calibration
anchor that breaks the recursive AI trust contamination loop.

Usage:
    python scripts/ingest_ground_truth.py \\
        --finding-id XTR-001 \\
        --outcome accepted \\
        --severity high \\
        [--assumption-count 2] \\
        [--assumptions "attacker controls tx ordering" "liquidity stable during exploit"] \\
        [--rejection-reason "..."] \\
        [--recorded-by human]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, get_audit_meta

EVAL_DIR = audit_path("data/evaluation")
OUTPUT_DIR = audit_path("output")
TRIAGE_DIR = audit_path("data/triage")

VALID_OUTCOMES = {"accepted", "rejected", "downgraded", "duplicate"}
VALID_SEVERITIES = {"critical", "high", "medium", "low", "invalid"}
VALID_RECORDED_BY = {"human", "contest_result"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_finding_context(finding_id: str) -> dict:
    ctx: dict = {"finding_id": finding_id}

    merged_path = OUTPUT_DIR / "merged_findings.json"
    if merged_path.exists():
        try:
            data = json.loads(merged_path.read_text())
            for f in data.get("findings", []):
                if f.get("id") == finding_id:
                    ctx["title"] = f.get("title", "")
                    ctx["vuln_type"] = f.get("vuln_type", "")
                    ctx["claimed_severity"] = f.get("severity", "")
                    ctx["agent"] = f.get("agent", f.get("_source_agent", ""))
                    break
        except json.JSONDecodeError:
            pass

    for fname in ["submit.jsonl", "poc_required.jsonl", "rejected.jsonl", "downgraded.jsonl"]:
        tpath = TRIAGE_DIR / fname
        if not tpath.exists():
            continue
        for line in tpath.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("finding_id") == finding_id:
                    ctx["pipeline_triage_status"] = rec.get("triage_status", "")
                    ctx["pipeline_severity"] = rec.get("recommended_severity", "")
                    score = rec.get("score")
                    ctx["pipeline_score"] = score.get("total") if isinstance(score, dict) else score
                    break
            except json.JSONDecodeError:
                continue
        if "pipeline_triage_status" in ctx:
            break

    return ctx


def load_existing(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    records: dict[str, dict] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            fid = rec.get("finding_id", "")
            if fid:
                records[fid] = rec
        except json.JSONDecodeError:
            continue
    return records


def main():
    parser = argparse.ArgumentParser(description="Ingest a ground-truth finding outcome")
    parser.add_argument("--finding-id", required=True)
    parser.add_argument("--outcome", required=True, choices=list(VALID_OUTCOMES))
    parser.add_argument("--severity", required=True, choices=list(VALID_SEVERITIES))
    parser.add_argument("--assumption-count", type=int, default=None)
    parser.add_argument("--assumptions", nargs="*", default=[],
                        help="List of critical assumptions the exploit depends on")
    parser.add_argument("--rejection-reason", default="")
    parser.add_argument("--recorded-by", default="human", choices=list(VALID_RECORDED_BY))
    args = parser.parse_args()

    meta = get_audit_meta()
    source_audit = meta.get("audit_id", "unknown")

    ctx = load_finding_context(args.finding_id)
    if not ctx.get("title"):
        print(f"  [warn] No finding data found for {args.finding_id} in this audit — recording partial entry")

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    gt_path = EVAL_DIR / "ground_truth.jsonl"

    existing = load_existing(gt_path)
    if args.finding_id in existing:
        print(f"  [info] Overwriting existing entry for {args.finding_id}")

    assumption_count = args.assumption_count
    if assumption_count is None:
        assumption_count = len(args.assumptions) if args.assumptions else 0

    record = {
        "finding_id":          args.finding_id,
        "source_audit":        source_audit,
        "title":               ctx.get("title", ""),
        "vuln_type":           ctx.get("vuln_type", ""),
        "claimed_severity":    ctx.get("claimed_severity", ""),
        "agent":               ctx.get("agent", ""),
        "ground_truth_outcome":   args.outcome,
        "ground_truth_severity":  args.severity,
        "assumption_count":       assumption_count,
        "critical_assumptions":   args.assumptions or [],
        "rejection_reason":       args.rejection_reason,
        "pipeline_triage_status": ctx.get("pipeline_triage_status", ""),
        "pipeline_severity":      ctx.get("pipeline_severity", ""),
        "pipeline_score":         ctx.get("pipeline_score"),
        "recorded_by":            args.recorded_by,
        "recorded_at":            _now(),
    }

    existing[args.finding_id] = record

    with gt_path.open("w") as fh:
        for rec in existing.values():
            fh.write(json.dumps(rec) + "\n")

    outcome_sev = f"{args.outcome}/{args.severity}"
    print(f"Ground Truth Ingested — {args.finding_id}")
    print(f"  Outcome:    {outcome_sev}")
    print(f"  Assumptions: {assumption_count}")
    if args.assumptions:
        for a in args.assumptions:
            print(f"    • {a}")
    print(f"  Written:    {gt_path}  ({len(existing)} total entries)")


if __name__ == "__main__":
    main()
