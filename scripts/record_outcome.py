#!/usr/bin/env python3
"""
record_outcome.py — Unified, human-driven front door for capturing a finding's REAL outcome.

This is the keystone of the feedback loop. It captures the full terminal outcome of a finding
(accepted / duplicate / invalid / downgraded / escalated / paid / closed) plus its provenance,
records it through the SINGLE sanctioned ground-truth writer, feeds severity learning when the
severity changed, and stages auto-learning candidates for human promotion.

Principle: a system that cannot measure its own false-positive rate or recall cannot be tuned.

Human-only. Outcomes are NEVER inferred by AI — you supply the verdict and the evidence. A record
without provenance (evidence_class / source_file / evidence) is routed to needs_human_review.jsonl
instead of ground truth.

Usage:
    python scripts/record_outcome.py \\
        --finding-id GL-001 --outcome invalid --severity invalid \\
        --evidence-class fork_confirmed \\
        --source-file audits/gearbox-2026-05/data/runtime_poc/results.jsonl \\
        --evidence "negative-control PoC shows bot cannot escalate permissions" \\
        [--claimed-severity high] [--paid-amount 5000] [--protocol-response "..."] \\
        [--duplicate-of-report "#3329553"] [--no-learn]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ingest_ground_truth as gt
from audit_context import audit_path, get_audit_meta

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "qa": 4, "invalid": 5}


def _append_severity_learning(finding_id: str, claimed: str, final: str, reason: str,
                              vuln_type: str) -> None:
    """Mirror ingest_judging_results' severity_history shape (feeds calibrate_severity.py)."""
    import json
    from datetime import datetime, timezone
    path = audit_path("data/learning", "severity_history.jsonl")
    rec = {
        "finding_id": finding_id,
        "claimed_severity": claimed,
        "final_judged_severity": final,
        "reason_for_change": reason,
        "bug_family": vuln_type,
        "lesson": f"{claimed}→{final}: {reason}",
        "source": "record_outcome",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    with path.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Record a finding's real outcome (human-only)")
    ap.add_argument("--finding-id", required=True)
    ap.add_argument("--outcome", required=True, choices=sorted(gt.VALID_OUTCOMES))
    ap.add_argument("--severity", required=True, choices=sorted(gt.VALID_SEVERITIES),
                    help="The FINAL ground-truth severity (use 'invalid' for invalid/duplicate)")
    ap.add_argument("--claimed-severity", default="",
                    help="What the pipeline claimed (enables severity-change learning)")
    # Provenance (required for a ground-truth write)
    ap.add_argument("--evidence-class", default="", choices=[""] + sorted(gt.VALID_EVIDENCE_CLASSES))
    ap.add_argument("--source-file", default="")
    ap.add_argument("--evidence", default="", help="One-line evidence summary")
    ap.add_argument("--confidence", type=float, default=None)
    # Extra outcome detail
    ap.add_argument("--paid-amount", default="")
    ap.add_argument("--protocol-response", default="")
    ap.add_argument("--closed-reason", default="")
    ap.add_argument("--duplicate-of-report", default="")
    ap.add_argument("--rejection-reason", default="")
    ap.add_argument("--assumptions", nargs="*", default=[])
    ap.add_argument("--no-learn", action="store_true", help="Skip staging auto-learning candidates")
    ap.add_argument("--no-autopromote", action="store_true",
                    help="Stage candidates but skip recall-safe auto-promotion")
    ap.add_argument("--eval", action="store_true",
                    help="Eval/blind context — auto-promotion honors config disable_in_eval")
    args = ap.parse_args()

    meta = get_audit_meta()
    ctx = gt.load_finding_context(args.finding_id)
    outcome = gt._outcome_alias(args.outcome)

    record = {
        "finding_id":          args.finding_id,
        "source_audit":        meta.get("audit_id", "unknown"),
        "title":               ctx.get("title", ""),
        "vuln_type":           ctx.get("vuln_type", ""),
        "claimed_severity":    args.claimed_severity or ctx.get("claimed_severity", ""),
        "agent":               ctx.get("agent", ""),
        "ground_truth_outcome":   outcome,
        "ground_truth_severity":  args.severity,
        "assumption_count":       len(args.assumptions),
        "critical_assumptions":   args.assumptions or [],
        "rejection_reason":       args.rejection_reason,
        "pipeline_triage_status": ctx.get("pipeline_triage_status", ""),
        "pipeline_severity":      ctx.get("pipeline_severity", ""),
        "pipeline_score":         ctx.get("pipeline_score"),
        "evidence_class":         args.evidence_class,
        "source_file":            args.source_file,
        "evidence_summary":       args.evidence,
        "confidence":             args.confidence,
        "paid_amount":            args.paid_amount,
        "protocol_response":      args.protocol_response,
        "closed_reason":          args.closed_reason,
        "duplicate_of_report":    args.duplicate_of_report,
        "recorded_by":            "human",
        "recorded_at":            gt._now(),
    }

    written, dest = gt.write_outcome(record)   # SINGLE write path
    if not written:
        print(f"  [needs-human-review] {args.finding_id}: insufficient provenance → {dest}")
        print(f"  Provide --evidence-class, --source-file and --evidence to record ground truth.")
        return 1

    print(f"Outcome recorded — {args.finding_id}: {outcome}/{args.severity} [{args.evidence_class}]")
    print(f"  Evidence: {args.evidence}  (src: {args.source_file})")
    print(f"  Ground truth: {dest}")

    # Severity-change learning (only when we have both claimed and final and they differ)
    claimed = (args.claimed_severity or ctx.get("claimed_severity", "")).lower()
    final = args.severity.lower()
    if claimed and final and claimed in SEV_ORDER and final in SEV_ORDER and claimed != final:
        reason = args.rejection_reason or args.evidence or "outcome recorded"
        _append_severity_learning(args.finding_id, claimed, final, reason, ctx.get("vuln_type", ""))
        print(f"  Severity learning: {claimed}→{final} appended to severity_history.jsonl")

    # Stage auto-learning candidates (deterministic; → data/learning/_proposed/)
    if not args.no_learn:
        try:
            import derive_learning
            staged = derive_learning.derive_from_record(record)
            if staged:
                print(f"  Auto-learning: staged {staged} candidate(s) in data/learning/_proposed/.")
            # Recall-safe AUTO promotion (confirmed + recall-safe + dedup). Validated candidates move
            # to the separate auto-rules file; anything that fails stays staged for promote_learning.py.
            if not args.no_autopromote:
                import auto_promote_learning
                s = auto_promote_learning.run(eval_mode=args.eval)
                if s.get("skipped"):
                    print(f"  Auto-promote: skipped ({s['skipped']}).")
                elif s.get("promoted") or s.get("left_staged"):
                    print(f"  Auto-promote: promoted {s['promoted']} (recall-safe), "
                          f"left {s['left_staged']} staged for human — reasons: {s['reasons']}")
        except Exception as e:
            print(f"  [warn] auto-learning staging skipped: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
