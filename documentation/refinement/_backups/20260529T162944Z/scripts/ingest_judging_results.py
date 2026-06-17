#!/usr/bin/env python3
"""
ingest_judging_results.py — Record actual contest judging outcomes.

Appends a severity learning record to data/learning/severity_history.jsonl
so future calibrate_severity.py runs can learn from past mistakes.

Usage:
    python scripts/ingest_judging_results.py \\
        --finding-id AR-001 \\
        --claimed-severity high \\
        --judged-severity medium \\
        --contest k2-code4rena-2026-04 \\
        --reason "impact was indirect, bounded by close factor" \\
        --impact-type accounting_error \\
        --attacker-model unprivileged
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

LEARN_DIR = audit_path("data/learning")


def main():
    parser = argparse.ArgumentParser(
        description="Record an actual contest judging outcome for severity calibration learning"
    )
    parser.add_argument("--finding-id",       required=True)
    parser.add_argument("--claimed-severity", required=True,
                        choices=["critical", "high", "medium", "low", "qa", "invalid"])
    parser.add_argument("--judged-severity",  required=True,
                        choices=["critical", "high", "medium", "low", "qa", "invalid"])
    parser.add_argument("--contest",          required=True,
                        help="Contest identifier, e.g. k2-code4rena-2026-04")
    parser.add_argument("--reason",           required=True,
                        help="Judge's stated reason for any severity change")
    parser.add_argument("--impact-type",      default="unknown",
                        help="One of: fund_loss, bad_debt, dos, accounting_error, reentrancy, other")
    parser.add_argument("--attacker-model",   default="unknown",
                        help="One of: unprivileged, borrower, supplier, admin, liquidator, other")
    parser.add_argument("--bug-family",       default="",
                        help="Optional: arithmetic, reentrancy, oracle, access_control, logic, dos")
    parser.add_argument("--lesson",           default="",
                        help="Optional: the key lesson to carry forward")
    args = parser.parse_args()

    LEARN_DIR.mkdir(parents=True, exist_ok=True)
    history_path = LEARN_DIR / "severity_history.jsonl"

    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "qa": 4, "invalid": 5}
    claimed_idx = sev_order.get(args.claimed_severity, 9)
    judged_idx  = sev_order.get(args.judged_severity,  9)

    if not args.lesson:
        if judged_idx > claimed_idx:
            lesson = (
                f"Claimed {args.claimed_severity} was downgraded to {args.judged_severity}. "
                f"Reason: {args.reason}. "
                f"Future findings of type {args.impact_type} with {args.attacker_model} attacker "
                f"should default to {args.judged_severity}."
            )
        elif judged_idx < claimed_idx:
            lesson = (
                f"Claimed {args.claimed_severity} was upgraded to {args.judged_severity}. "
                f"Reason: {args.reason}."
            )
        else:
            lesson = f"Severity confirmed at {args.judged_severity}. Reason: {args.reason}."
    else:
        lesson = args.lesson

    record = {
        "finding_id":           args.finding_id,
        "claimed_severity":     args.claimed_severity,
        "final_judged_severity": args.judged_severity,
        "contest":              args.contest,
        "reason_for_change":    args.reason,
        "bug_family":           args.bug_family or args.impact_type,
        "attacker_model":       args.attacker_model,
        "impact_type":          args.impact_type,
        "lesson":               lesson,
        "date":                 datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }

    with history_path.open("a") as fh:
        fh.write(json.dumps(record) + "\n")

    change = ""
    if judged_idx > claimed_idx:
        change = f"  ⚠  DOWNGRADE: {args.claimed_severity} → {args.judged_severity}"
    elif judged_idx < claimed_idx:
        change = f"  ↑  UPGRADE: {args.claimed_severity} → {args.judged_severity}"
    else:
        change = f"  ✓  CONFIRMED: {args.claimed_severity}"

    print(f"Recorded judging result for {args.finding_id}")
    print(change)
    print(f"  Contest: {args.contest}")
    print(f"  Reason:  {args.reason}")
    print(f"  Lesson:  {lesson}")
    print(f"  Appended → {history_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
