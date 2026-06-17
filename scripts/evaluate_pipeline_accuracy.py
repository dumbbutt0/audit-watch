#!/usr/bin/env python3
"""
evaluate_pipeline_accuracy.py — Measure pipeline accuracy against ground truth.

Reads data/evaluation/ground_truth.jsonl and compares outcomes against the
pipeline's triage records. Prints a metrics table and writes
data/evaluation/accuracy_report.json.

Exits 0 even when corpus is empty — prints a "no data yet" message.

Usage:
    python scripts/evaluate_pipeline_accuracy.py
    python scripts/evaluate_pipeline_accuracy.py --audit-id xterio-2026-05
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, get_audit_meta

EVAL_DIR  = audit_path("data/evaluation")
TRIAGE_DIR = audit_path("data/triage")
FP_DIR    = audit_path("data/fp_autopsies")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return records


def load_ground_truth() -> list[dict]:
    return load_jsonl(EVAL_DIR / "ground_truth.jsonl")


def load_pipeline_outcomes() -> dict[str, dict]:
    """Build a map of finding_id → pipeline outcome from all triage buckets."""
    outcomes: dict[str, dict] = {}
    bucket_map = {
        "submit":       "accepted",
        "poc_required": "accepted",
        "downgraded":   "downgraded",
        "merged":       "duplicate",
        "rejected":     "rejected",
    }
    for fname, pipeline_outcome in bucket_map.items():
        for rec in load_jsonl(TRIAGE_DIR / f"{fname}.jsonl"):
            fid = rec.get("finding_id", "")
            if fid and fid not in outcomes:
                outcomes[fid] = {
                    "pipeline_outcome":  pipeline_outcome,
                    "pipeline_severity": rec.get("recommended_severity", ""),
                    "pipeline_score":    rec.get("score", {}).get("total"),
                    "invalidation_tags": rec.get("invalidation_tags", []),
                    "triage_status":     rec.get("triage_status", ""),
                }
    return outcomes


def load_gate_results() -> dict[str, dict]:
    return {
        rec["finding_id"]: rec
        for rec in load_jsonl(TRIAGE_DIR / "gate_results.jsonl")
        if "finding_id" in rec
    }


def _outcome_match(gt_outcome: str, pipeline_outcome: str) -> bool:
    """True if pipeline outcome agrees with ground truth."""
    # submitted/poc_required both map to "accepted"
    gt_norm = "accepted" if gt_outcome in ("accepted",) else gt_outcome
    pip_norm = "accepted" if pipeline_outcome in ("accepted",) else pipeline_outcome
    return gt_norm == pip_norm


def _sev_match(gt_sev: str, pip_sev: str) -> bool:
    return gt_sev.lower() == pip_sev.lower()


def compute_metrics(ground_truth: list[dict], pipeline: dict[str, dict],
                    gates: dict[str, dict]) -> dict:
    if not ground_truth:
        return {}

    total = len(ground_truth)
    outcome_matches = 0
    sev_matches = 0
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    gate_correct_rejects = 0
    gate_total_rejects = 0
    missing_from_pipeline = 0

    for gt in ground_truth:
        fid = gt["finding_id"]
        pip = pipeline.get(fid)
        if not pip:
            missing_from_pipeline += 1
            if gt["ground_truth_outcome"] in ("accepted", "downgraded"):
                false_negatives += 1
            continue

        if _outcome_match(gt["ground_truth_outcome"], pip["pipeline_outcome"]):
            outcome_matches += 1

        if _sev_match(gt["ground_truth_severity"], pip["pipeline_severity"]):
            sev_matches += 1

        gt_accepted = gt["ground_truth_outcome"] in ("accepted", "downgraded")
        pip_accepted = pip["pipeline_outcome"] in ("accepted",)

        if gt_accepted and pip_accepted:
            true_positives += 1
        elif not gt_accepted and pip_accepted:
            false_positives += 1
        elif gt_accepted and not pip_accepted:
            false_negatives += 1

        # Gate precision: if gate REJECTed, was the ground truth also rejected?
        gate = gates.get(fid, {})
        if gate.get("overall_verdict") == "REJECT":
            gate_total_rejects += 1
            if gt["ground_truth_outcome"] == "rejected":
                gate_correct_rejects += 1

    n = total - missing_from_pipeline
    if n == 0:
        return {"total": total, "missing_from_pipeline": missing_from_pipeline}

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else None
    recall    = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else None
    gate_prec = gate_correct_rejects / gate_total_rejects if gate_total_rejects > 0 else None

    return {
        "total":                     total,
        "evaluated":                 n,
        "missing_from_pipeline":     missing_from_pipeline,
        "outcome_accuracy":          round(outcome_matches / n, 3),
        "severity_accuracy":         round(sev_matches / n, 3),
        "true_positives":            true_positives,
        "false_positives":           false_positives,
        "false_negatives":           false_negatives,
        "precision":                 round(precision, 3) if precision is not None else None,
        "recall":                    round(recall, 3) if recall is not None else None,
        "gate_total_rejects":        gate_total_rejects,
        "gate_correct_rejects":      gate_correct_rejects,
        "gate_precision":            round(gate_prec, 3) if gate_prec is not None else None,
        "targets": {
            "outcome_accuracy":      "> 0.80",
            "false_positive_rate":   "< 0.10",
            "severity_accuracy":     "> 0.70",
            "gate_precision":        "> 0.90",
        },
    }


def print_report(metrics: dict, ground_truth: list[dict]) -> None:
    print("\nPipeline Accuracy Report")
    print("=" * 55)

    if not metrics:
        print("  No ground truth entries found.")
        print(f"  Run: python scripts/ingest_ground_truth.py --finding-id <ID> --outcome <outcome> --severity <sev>")
        print("=" * 55)
        return

    n = metrics.get("evaluated", 0)
    total = metrics.get("total", 0)
    missing = metrics.get("missing_from_pipeline", 0)

    print(f"  Ground truth entries: {total}  (evaluated: {n}, missing from pipeline: {missing})")
    print()

    def _fmt(val, target: str = "") -> str:
        if val is None:
            return f"{'n/a':<10} {target}"
        return f"{val:<10.3f} {target}"

    targets = metrics.get("targets", {})
    print(f"  {'Metric':<30} {'Value':<10} Target")
    print(f"  {'-'*55}")
    print(f"  {'Outcome accuracy':<30} {_fmt(metrics.get('outcome_accuracy'), targets.get('outcome_accuracy',''))}")
    print(f"  {'Severity accuracy':<30} {_fmt(metrics.get('severity_accuracy'), targets.get('severity_accuracy',''))}")

    tp = metrics.get('true_positives', 0)
    fp = metrics.get('false_positives', 0)
    fn = metrics.get('false_negatives', 0)
    fp_rate = fp / (fp + tp) if (fp + tp) > 0 else None
    print(f"  {'False positive rate':<30} {_fmt(fp_rate, targets.get('false_positive_rate',''))}")
    print(f"  {'Gate precision':<30} {_fmt(metrics.get('gate_precision'), targets.get('gate_precision',''))}")
    print()
    print(f"  True positives:  {tp}   False positives: {fp}   False negatives: {fn}")

    if ground_truth:
        assumption_counts = [gt.get("assumption_count", 0) for gt in ground_truth if gt.get("assumption_count")]
        if assumption_counts:
            avg_assumptions = sum(assumption_counts) / len(assumption_counts)
            accepted = [gt for gt in ground_truth if gt.get("ground_truth_outcome") == "accepted"]
            rejected_gt = [gt for gt in ground_truth if gt.get("ground_truth_outcome") == "rejected"]
            acc_assumptions = [gt.get("assumption_count", 0) for gt in accepted if gt.get("assumption_count") is not None]
            rej_assumptions = [gt.get("assumption_count", 0) for gt in rejected_gt if gt.get("assumption_count") is not None]
            print()
            print(f"  Assumption analysis:")
            print(f"    Average assumption count:           {avg_assumptions:.1f}")
            if acc_assumptions:
                print(f"    Avg assumptions (accepted findings): {sum(acc_assumptions)/len(acc_assumptions):.1f}")
            if rej_assumptions:
                print(f"    Avg assumptions (rejected findings): {sum(rej_assumptions)/len(rej_assumptions):.1f}")

    print("=" * 55)


def main():
    parser = argparse.ArgumentParser(description="Evaluate pipeline accuracy against ground truth")
    parser.add_argument("--audit-id", help="Specific audit to evaluate (defaults to active)")
    args = parser.parse_args()

    meta = get_audit_meta()
    audit_id = args.audit_id or meta.get("audit_id", "unknown")
    print(f"Pipeline Accuracy Evaluation — {audit_id}")

    ground_truth = load_ground_truth()
    pipeline = load_pipeline_outcomes()
    gates = load_gate_results()

    metrics = compute_metrics(ground_truth, pipeline, gates)
    print_report(metrics, ground_truth)

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "audit_id":     audit_id,
        "generated_at": _now(),
        "corpus_size":  len(ground_truth),
        "metrics":      metrics,
    }
    out_path = EVAL_DIR / "accuracy_report.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(f"\n  Written: {out_path}")


if __name__ == "__main__":
    main()
