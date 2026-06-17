#!/usr/bin/env python3
"""
run_specialist_review.py — Orchestrate the full specialist review pipeline.

Runs: exploitability → duplicate_risk → severity_calibration →
      runtime_poc → judge_simulation, then prints the decision matrix.

Usage:
    python scripts/run_specialist_review.py             # all findings
    python scripts/run_specialist_review.py --finding-id AR-001
    python scripts/run_specialist_review.py --from-step 3
    python scripts/run_specialist_review.py --all --force
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from decision_logic import compute_finding_action

TRIAGE_DIR  = audit_path("data/triage")
EXPLOIT_DIR = audit_path("data/exploitability")
DUP_DIR     = audit_path("data/duplicates")
SEV_DIR     = audit_path("data/severity")
POC_DIR     = audit_path("data/runtime_poc")
JUDGE_DIR   = audit_path("data/judge_simulation")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return items


def run_step(label: str, script: str, finding_id: str | None, force: bool) -> bool:
    print(f"\n{'─'*65}")
    print(f"  STEP: {label}")
    print(f"{'─'*65}")

    cmd = [sys.executable, script]
    if finding_id:
        cmd += ["--finding-id", finding_id]
    else:
        cmd += ["--all"]
    if force:
        cmd += ["--force"]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n  [warn] {script} exited with code {result.returncode}")
        return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Decision matrix
# ─────────────────────────────────────────────────────────────────────────────

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "qa": 4, "invalid": 5, "?": 9}

# compute_action is sourced from decision_logic.py (single source of truth)
compute_action = compute_finding_action


def print_decision_matrix(finding_ids: list[str]) -> None:
    exploit_map = {r["finding_id"]: r for r in load_jsonl(EXPLOIT_DIR / "models.jsonl")
                   if "finding_id" in r}
    dup_map     = {r["finding_id"]: r for r in load_jsonl(DUP_DIR / "risk.jsonl")
                   if "finding_id" in r}
    sev_map     = {r["finding_id"]: r for r in load_jsonl(SEV_DIR / "calibrated.jsonl")
                   if "finding_id" in r}
    poc_map     = {r["finding_id"]: r for r in load_jsonl(POC_DIR / "results.jsonl")
                   if "finding_id" in r}
    judge_map   = {r["finding_id"]: r for r in load_jsonl(JUDGE_DIR / "results.jsonl")
                   if "finding_id" in r}

    border = "─" * 97
    header = (
        f"│  {'Finding':<13}│ {'Exploit':^8}│ {'Dup Risk':^10}│ {'Sev Calib':^11}│"
        f" {'PoC Lvl':^8}│ {'Judge Outcome':^17}│ {'Action':^10}│"
    )

    print(f"\n{'='*97}")
    print(f"  Specialist Review — Decision Matrix")
    print(f"{'='*97}")
    print(f"┌{border}┐")
    print(f"{header}")
    print(f"├{border}┤")

    for fid in finding_ids:
        exploit   = exploit_map.get(fid, {})
        dup       = dup_map.get(fid, {})
        sev       = sev_map.get(fid, {})
        poc       = poc_map.get(fid, {})
        judge     = judge_map.get(fid, {})

        e_score   = exploit.get("exploitability_score", "—")
        dup_risk  = dup.get("duplicate_risk", "—")
        cal_sev   = sev.get("calibrated_severity", "—")
        poc_level = poc.get("runtime_level", 0) if poc else 0
        judge_out = judge.get("predicted_outcome", "—")

        action = compute_action(
            int(e_score) if str(e_score).isdigit() else 0,
            str(dup_risk),
            str(cal_sev),
            int(poc_level) if str(poc_level).isdigit() else 0,
            str(judge_out),
        )

        action_fmt = {
            "SUBMIT":    "✅ SUBMIT",
            "REVISE":    "✏ REVISE",
            "POC_FIRST": "🔬 POC_FIRST",
            "MERGE":     "⊕ MERGE",
            "DROP":      "✗ DROP",
        }.get(action, action)

        print(
            f"│  {fid:<13}│ {str(e_score):^8}│ {str(dup_risk):^10}│ {str(cal_sev):^11}│"
            f" {str(poc_level):^8}│ {str(judge_out):^17}│ {action_fmt:<10}│"
        )

    print(f"└{border}┘")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

STEPS = [
    (1, "Exploitability Modeling",    "scripts/model_exploitability.py"),
    (2, "Duplicate Risk Estimation",  "scripts/estimate_duplicate_risk.py"),
    (3, "Severity Calibration",       "scripts/calibrate_severity.py"),
    (4, "Runtime PoC Execution",      "scripts/run_integrated_poc.py"),
    (5, "Judge Simulation",           "scripts/judge_simulate.py"),
]


def main():
    parser = argparse.ArgumentParser(description="Specialist Review Pipeline Orchestrator")
    parser.add_argument("--finding-id",  default=None, help="Run on a single finding")
    parser.add_argument("--all",         action="store_true", help="Run on all findings")
    parser.add_argument("--from-step",   type=int, default=1,
                        help="Resume from step N (1–5)")
    parser.add_argument("--force",       action="store_true", help="Re-run all steps")
    args = parser.parse_args()

    if not args.finding_id and not args.all:
        args.all = True  # default to all

    # Print pipeline state
    submit_count   = sum(1 for _ in load_jsonl(TRIAGE_DIR / "submit.jsonl"))
    poc_req_count  = sum(1 for _ in load_jsonl(TRIAGE_DIR / "poc_required.jsonl"))
    total          = submit_count + poc_req_count

    print("="*65)
    print("  Smart Contract Auditor — Specialist Review Pipeline")
    print("="*65)
    if args.finding_id:
        print(f"  Mode:       single finding ({args.finding_id})")
    else:
        print(f"  Mode:       all findings")
    print(f"  Submit:     {submit_count} findings")
    print(f"  PoC req:    {poc_req_count} findings")
    print(f"  Total:      {total} findings")
    print(f"  From step:  {args.from_step}")
    print(f"  Force:      {args.force}")

    # Run steps
    for step_num, label, script in STEPS:
        if step_num < args.from_step:
            print(f"\n  [skip] Step {step_num}: {label}")
            continue
        success = run_step(label, script, args.finding_id, args.force)
        if not success and step_num <= 2:
            print(f"\n[abort] Step {step_num} failed — halting pipeline")
            return 1

    # Collect finding IDs to show in matrix
    triage_items = (
        load_jsonl(TRIAGE_DIR / "submit.jsonl") +
        load_jsonl(TRIAGE_DIR / "poc_required.jsonl")
    )
    if args.finding_id:
        fids = [args.finding_id]
    else:
        fids = [t.get("finding_id", "") for t in triage_items if t.get("finding_id")]

    print_decision_matrix(fids)

    return 0


if __name__ == "__main__":
    sys.exit(main())
