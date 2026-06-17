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

# Expanded terminal outcomes (2026-05 feedback-loop). "rejected" kept as an alias of "invalid".
VALID_OUTCOMES = {"accepted", "duplicate", "invalid", "downgraded", "escalated",
                  "paid", "closed", "rejected"}
VALID_SEVERITIES = {"critical", "high", "medium", "low", "invalid"}
VALID_RECORDED_BY = {"human", "contest_result"}

# Provenance — every ground-truth entry must say WHERE the outcome came from.
# AI must never infer an outcome; ambiguous evidence is routed to needs_human_review.jsonl.
VALID_EVIDENCE_CLASSES = {"human_confirmed", "platform_confirmed", "fork_confirmed", "manual_entry"}


def _outcome_alias(outcome: str) -> str:
    """Normalize legacy 'rejected' to 'invalid'."""
    return "invalid" if outcome == "rejected" else outcome


def write_outcome(record: dict, eval_dir: "Path | str | None" = None) -> tuple[bool, str]:
    """THE single write path to ground_truth.jsonl (importable by record_outcome.py / backfill).

    Enforces provenance: a record missing evidence_class/source_file/evidence_summary is NOT
    written to ground truth — it is appended to needs_human_review.jsonl and reported back.

    `eval_dir` lets a caller target a SPECIFIC audit's data/evaluation/ (used by the cross-audit
    backfill) without switching the active audit. Defaults to the active audit's EVAL_DIR.
    Returns (written, destination).
    """
    ed = Path(eval_dir) if eval_dir else EVAL_DIR
    fid = record.get("finding_id", "")
    missing = [k for k in ("evidence_class", "source_file", "evidence_summary")
               if not str(record.get(k, "")).strip()]
    if record.get("evidence_class") and record["evidence_class"] not in VALID_EVIDENCE_CLASSES:
        missing.append(f"evidence_class∈{sorted(VALID_EVIDENCE_CLASSES)}")

    ed.mkdir(parents=True, exist_ok=True)
    if missing:
        nh_path = ed / "needs_human_review.jsonl"
        record = {**record, "_missing_provenance": missing, "_routed_at": _now()}
        with nh_path.open("a") as fh:
            fh.write(json.dumps(record) + "\n")
        return False, str(nh_path)

    gt_path = ed / "ground_truth.jsonl"
    existing = load_existing(gt_path)
    existing[fid] = record
    with gt_path.open("w") as fh:
        for rec in existing.values():
            fh.write(json.dumps(rec) + "\n")
    return True, str(gt_path)


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
    # Provenance (required for a ground-truth write; missing → needs_human_review.jsonl)
    parser.add_argument("--evidence-class", default="", choices=[""] + sorted(VALID_EVIDENCE_CLASSES))
    parser.add_argument("--source-file", default="", help="Path/artifact evidencing this outcome")
    parser.add_argument("--evidence", default="", help="One-line evidence summary")
    parser.add_argument("--confidence", type=float, default=None, help="0.0–1.0")
    parser.add_argument("--paid-amount", default="")
    parser.add_argument("--protocol-response", default="")
    parser.add_argument("--closed-reason", default="")
    parser.add_argument("--duplicate-of-report", default="")
    args = parser.parse_args()

    meta = get_audit_meta()
    source_audit = meta.get("audit_id", "unknown")

    ctx = load_finding_context(args.finding_id)
    if not ctx.get("title"):
        print(f"  [warn] No finding data found for {args.finding_id} in this audit — recording partial entry")

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
        "ground_truth_outcome":   _outcome_alias(args.outcome),
        "ground_truth_severity":  args.severity,
        "assumption_count":       assumption_count,
        "critical_assumptions":   args.assumptions or [],
        "rejection_reason":       args.rejection_reason,
        "pipeline_triage_status": ctx.get("pipeline_triage_status", ""),
        "pipeline_severity":      ctx.get("pipeline_severity", ""),
        "pipeline_score":         ctx.get("pipeline_score"),
        # Provenance
        "evidence_class":         args.evidence_class,
        "source_file":            args.source_file,
        "evidence_summary":       args.evidence,
        "confidence":             args.confidence,
        "paid_amount":            args.paid_amount,
        "protocol_response":      args.protocol_response,
        "closed_reason":          args.closed_reason,
        "duplicate_of_report":    args.duplicate_of_report,
        "recorded_by":            args.recorded_by,
        "recorded_at":            _now(),
    }

    written, dest = write_outcome(record)
    if written:
        total = len(load_existing(EVAL_DIR / "ground_truth.jsonl"))
        print(f"Ground Truth Ingested — {args.finding_id}")
        print(f"  Outcome:    {_outcome_alias(args.outcome)}/{args.severity}  "
              f"[{args.evidence_class}]")
        print(f"  Evidence:   {args.evidence}  (src: {args.source_file})")
        print(f"  Written:    {dest}  ({total} total entries)")
    else:
        print(f"  [needs-human-review] {args.finding_id}: insufficient provenance — "
              f"routed to {dest} (not written to ground truth).")


if __name__ == "__main__":
    main()
