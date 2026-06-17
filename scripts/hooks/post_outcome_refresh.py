#!/usr/bin/env python3
"""
post_outcome_refresh.py — WARN-ONLY hook: refresh metrics after a recorded outcome.

Intended trigger: PostToolUse on a Bash command running `record_outcome.py`.

After a human records a real outcome, the cross-audit metrics should reflect it immediately so
the calibration surface (and dashboard) stays current. This hook:
    • recomputes metrics by calling compute_metrics.main() (overwrites the read-only
      documentation/metrics/metrics.json + metrics_report.md — these are derived, not trusted).
    • reminds the operator if needs_human_review.jsonl still has pending dispositions and how many
      learning candidates are staged awaiting human promotion.

It deliberately does NOT run derive_learning over all records: record_outcome.py already stages
the candidate for the record it just wrote (record_outcome.py:131-137), so re-deriving here would
double-stage. This hook NEVER promotes learning, NEVER writes ground_truth.jsonl, and NEVER mutates
shared rules. It always exits 0.

Writes audits/<id>/data/gates/post_outcome_refresh.json.

Run manually:  python scripts/hooks/post_outcome_refresh.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _hooklib as h


def _refresh_metrics(dry_run: bool) -> str:
    if dry_run:
        return "skipped (dry-run)"
    try:
        import compute_metrics
        compute_metrics.main()  # writes metrics.json + metrics_report.md, returns 0
        return "metrics.json + metrics_report.md refreshed"
    except Exception as e:
        return f"refresh failed (non-fatal): {e}"


def _proposed_count() -> int:
    pdir = h.audit_file("data/learning", "_proposed")
    if pdir is None or not pdir.exists():
        return 0
    return sum(sum(1 for ln in p.read_text().splitlines() if ln.strip())
               for p in pdir.glob("*.jsonl"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Post-outcome metrics refresh (warn-only)")
    ap.add_argument("--dry-run", action="store_true", help="Print intent; refresh nothing")
    args = ap.parse_args()

    h.read_hook_input()  # drain stdin if invoked as a hook; outcome is already recorded

    nhr = h.load_jsonl(h.audit_file("data/evaluation", "needs_human_review.jsonl"))
    refresh = _refresh_metrics(args.dry_run)
    proposed = _proposed_count()

    summary = {
        "generated_at": h.now(),
        "metrics_refresh": refresh,
        "needs_human_review_pending": len(nhr),
        "unpromoted_learning_candidates": proposed,
        "note": "derive_learning NOT re-run here (record_outcome stages its own candidate); "
                "learning promotion is human-only via promote_learning.py.",
    }
    h.write_gate_artifact(["post_outcome_refresh.json"], summary, dry_run=args.dry_run)

    msgs = [f"metrics: {refresh}"]
    if nhr:
        msgs.append(f"{len(nhr)} finding(s) still in needs_human_review — disposition via record_outcome.py")
    if proposed:
        msgs.append(f"{proposed} learning candidate(s) staged — review with promote_learning.py (dry-run)")
    print("[audit-watch hook] " + "; ".join(msgs), file=sys.stderr)
    return h.ALLOW  # always allow


if __name__ == "__main__":
    sys.exit(main())
