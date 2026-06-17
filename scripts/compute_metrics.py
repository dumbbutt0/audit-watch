#!/usr/bin/env python3
"""
compute_metrics.py — Cross-audit pipeline metrics (READ-ONLY).

Aggregates the feedback-loop signal across ALL audit workspaces and answers the question the
38/50 evaluation flagged: can the pipeline measure its own false-positive rate and recall?

Reads (never writes ground truth):
    audits/<id>/data/evaluation/ground_truth.jsonl   — human-confirmed outcomes (the anchor)
    audits/<id>/data/triage/*.jsonl                  — what the pipeline decided
    audits/<id>/data/runtime_poc/results.jsonl       — PoC outcomes (status field)
    data/duplicate_registry.jsonl                    — confirmed duplicates

Emits:
    documentation/metrics/metrics.json       (machine)
    documentation/metrics/metrics_report.md  (human)

Every rate reports its denominator n; rates with n==0 are shown as "unmeasured (no ground truth)"
rather than a misleading 0.0 — honesty about what is actually measured.

Usage:  python scripts/compute_metrics.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import _AUDITS_DIR, _PROJECT_ROOT, list_audits, load_jsonl

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "qa": 4, "invalid": 5, "": 9}
ACCEPTED_TRUTH = {"accepted", "paid", "escalated"}
INVALID_TRUTH = {"invalid", "duplicate"}
PIPELINE_ACCEPTED_BUCKETS = {"submit.jsonl", "poc_required.jsonl"}


# Eval/benchmark corpora are excluded from real-world metrics. Their results are
# synthetic (contest backfill / blind-eval) and must not be reported as live performance.
_EVAL_SUFFIXES = (
    "-eval", "-eval2", "-strict-eval", "-blind", "-holdout", "-bench", "-shadow",
    "-semantic-tvl", "-liquidation-health", "-dry-run", "-strict-dry-run",
    "-refine-check", "-fresh",
)


# Eval/benchmark bases retained on disk only for integrity-pin anchors / symlink — their
# ground-truth is contest-backfill (synthetic) and must not feed real-world metrics.
_EVAL_AUDIT_IDS = {"beanstalk-2024-05", "size-credit-2024-06"}


def _is_eval_audit(aid: str) -> bool:
    return aid in _EVAL_AUDIT_IDS or any(aid.endswith(sfx) for sfx in _EVAL_SUFFIXES)


def _audit_ids() -> list[str]:
    ids = [a["audit_id"] for a in list_audits()]
    if _AUDITS_DIR.exists():
        for p in sorted(_AUDITS_DIR.iterdir()):
            if p.is_dir() and (p / "meta.json").exists() and p.name not in ids:
                ids.append(p.name)
    # Exclude eval/benchmark corpora — real-world metrics only.
    return [a for a in ids if not _is_eval_audit(a)]


def _rate(num: int, den: int):
    """Return {value, n} or {value: None, n:0, state: unmeasured}."""
    if den == 0:
        return {"value": None, "n": 0, "state": "unmeasured (no ground truth)"}
    return {"value": round(num / den, 3), "n": den, "numerator": num}


def _pipeline_decision(root: Path) -> dict[str, str]:
    """finding_id → 'accepted'|'rejected'|'downgraded'|'duplicate' from triage buckets."""
    out: dict[str, str] = {}
    tdir = root / "data" / "triage"
    if not tdir.is_dir():
        return out
    bucket_decision = {
        "submit.jsonl": "accepted", "poc_required.jsonl": "accepted",
        "downgraded.jsonl": "downgraded", "merged.jsonl": "duplicate", "rejected.jsonl": "rejected",
    }
    for fname, decision in bucket_decision.items():
        for rec in load_jsonl(tdir / fname):
            fid = rec.get("finding_id")
            if fid and fid not in out:
                out[fid] = decision
    return out


def compute() -> dict:
    """Build and return the cross-audit metrics dict (importable by the dashboard)."""
    audits = _audit_ids()
    # accumulators
    gt_total = 0
    truth_accepted = truth_invalid = truth_dup = 0
    downgrade_num = downgrade_den = 0
    fp_num = fp_den = 0          # among pipeline-accepted with ground truth, invalid/dup = FP
    recall_num = recall_den = 0  # among truly-valid, pipeline accepted
    poc_proved = poc_total = 0
    agent_stats = defaultdict(lambda: {"valid": 0, "invalid": 0})
    class_stats = defaultdict(lambda: {"valid": 0, "invalid": 0})
    per_audit = []

    for aid in audits:
        root = _AUDITS_DIR / aid
        gt = load_jsonl(root / "data" / "evaluation" / "ground_truth.jsonl")
        decisions = _pipeline_decision(root)
        poc = load_jsonl(root / "data" / "runtime_poc" / "results.jsonl")

        a_proved = sum(1 for r in poc if r.get("status") == "proved")
        a_poc = len(poc)
        poc_proved += a_proved
        poc_total += a_poc

        for r in gt:
            gt_total += 1
            outcome = r.get("ground_truth_outcome", "")
            fid = r.get("finding_id", "")
            agent = r.get("agent") or "unknown"
            vclass = r.get("vuln_type") or "unknown"
            is_valid = outcome in ACCEPTED_TRUTH
            is_invalid = outcome in INVALID_TRUTH

            if is_valid:
                truth_accepted += 1
                agent_stats[agent]["valid"] += 1
                class_stats[vclass]["valid"] += 1
            elif outcome == "duplicate":
                truth_dup += 1
                truth_invalid += 1
                agent_stats[agent]["invalid"] += 1
                class_stats[vclass]["invalid"] += 1
            elif is_invalid:
                truth_invalid += 1
                agent_stats[agent]["invalid"] += 1
                class_stats[vclass]["invalid"] += 1

            # downgrade: final severity strictly weaker than claimed
            claimed = (r.get("claimed_severity") or "").lower()
            final = (r.get("ground_truth_severity") or "").lower()
            if claimed in SEV_ORDER and final in SEV_ORDER and claimed and final:
                downgrade_den += 1
                if SEV_ORDER[final] > SEV_ORDER[claimed]:
                    downgrade_num += 1

            # FP rate: did the pipeline accept something that was invalid/dup?
            decision = decisions.get(fid)
            if decision == "accepted":
                fp_den += 1
                if is_invalid:
                    fp_num += 1
            # recall: of truly-valid findings, did the pipeline accept?
            if is_valid:
                recall_den += 1
                if decision == "accepted":
                    recall_num += 1

        per_audit.append({
            "audit_id": aid, "ground_truth_records": len(gt),
            "poc_proved": a_proved, "poc_total": a_poc,
        })

    def _rel(d):
        n = d["valid"] + d["invalid"]
        return {"reliability": round(d["valid"] / n, 3) if n else None, "n": n,
                "valid": d["valid"], "invalid": d["invalid"]}

    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audits_scanned": len(audits),
        "ground_truth_records": gt_total,
        "coverage_note": "Rates are over findings that HAVE a recorded human outcome. "
                         "Low ground_truth_records ⇒ metrics are directional, not yet robust.",
        "false_positive_rate": _rate(fp_num, fp_den),
        "recall_on_valid": _rate(recall_num, recall_den),
        "valid_finding_rate": _rate(truth_accepted, gt_total),
        "duplicate_rate": _rate(truth_dup, gt_total),
        "severity_downgrade_rate": _rate(downgrade_num, downgrade_den),
        "poc_success_rate": _rate(poc_proved, poc_total),
        "per_agent_reliability": {a: _rel(s) for a, s in sorted(agent_stats.items())},
        "per_bug_class_reliability": {c: _rel(s) for c, s in sorted(class_stats.items())},
        "per_audit": per_audit,
    }
    return metrics


def main() -> int:
    metrics = compute()

    out_dir = _PROJECT_ROOT / "documentation" / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    def _fmt(r):
        return f"{r['value']} (n={r['n']})" if r.get("value") is not None else r.get("state", "n/a")

    md = ["# Pipeline Metrics (cross-audit)\n",
          f"_Generated {metrics['generated_at']} · {metrics['audits_scanned']} audits · "
          f"{metrics['ground_truth_records']} ground-truth records._\n",
          f"> {metrics['coverage_note']}\n",
          "| Metric | Value |", "|---|---|",
          f"| False-positive rate | {_fmt(metrics['false_positive_rate'])} |",
          f"| Recall on valid findings | {_fmt(metrics['recall_on_valid'])} |",
          f"| Valid-finding rate | {_fmt(metrics['valid_finding_rate'])} |",
          f"| Duplicate rate | {_fmt(metrics['duplicate_rate'])} |",
          f"| Severity-downgrade rate | {_fmt(metrics['severity_downgrade_rate'])} |",
          f"| PoC success rate | {_fmt(metrics['poc_success_rate'])} |", ""]
    md.append("## Per-agent reliability (valid / valid+invalid, ground-truth'd only)\n")
    md.append("| Agent | Reliability | n |"); md.append("|---|---|---|")
    for a, s in metrics["per_agent_reliability"].items():
        md.append(f"| {a} | {s['reliability'] if s['reliability'] is not None else '—'} | {s['n']} |")
    md.append("\n## Per-bug-class reliability\n")
    md.append("| Bug class | Reliability | n |"); md.append("|---|---|---|")
    for c, s in metrics["per_bug_class_reliability"].items():
        md.append(f"| {c} | {s['reliability'] if s['reliability'] is not None else '—'} | {s['n']} |")
    (out_dir / "metrics_report.md").write_text("\n".join(md) + "\n")

    print(f"Metrics — {metrics['audits_scanned']} audits, {metrics['ground_truth_records']} ground-truth records")
    print(f"  FP rate:        {_fmt(metrics['false_positive_rate'])}")
    print(f"  Recall:         {_fmt(metrics['recall_on_valid'])}")
    print(f"  PoC success:    {_fmt(metrics['poc_success_rate'])}")
    print(f"  Written: {out_dir/'metrics.json'} + metrics_report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
