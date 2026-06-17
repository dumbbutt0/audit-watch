#!/usr/bin/env python3
"""
run_quality_checklist.py — evaluate the 7-question quality checklist for each
proved finding and write results to data/quality_checklist/results.jsonl.

Questions auto-answered from pipeline data where possible:
  Q1  Level 2 proved?     → data/runtime_poc/results.jsonl
  Q2  Level 3 proved?     → data/runtime_poc/results.jsonl
  Q3  Direct loss?        → data/judge_simulation/results.jsonl + triage
  Q4  Permissionless?     → data/exploitability/models.jsonl
  Q5  Victim realistic?   → data/triage/poc_required.jsonl + submit.jsonl
  Q6  Likely duplicate?   → data/duplicates/risk.jsonl
  Q7  One-sentence impact → must be manually confirmed (checks submissions/)

Usage:
  python scripts/run_quality_checklist.py --finding-id AR-001
  python scripts/run_quality_checklist.py --all
  python scripts/run_quality_checklist.py --all --report     # print table
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path


def load_jsonl(path: str) -> dict:
    """Load a JSONL file into a dict keyed by finding_id."""
    result = {}
    p = audit_path(path)
    if not p.exists():
        return result
    with open(p) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                fid = d.get("finding_id")
                if fid:
                    result[fid] = d
            except json.JSONDecodeError:
                pass
    return result


def check_q1(poc: dict) -> tuple[str, str]:
    """Q1: Level 2 proved?"""
    if poc.get("status") == "proved" and poc.get("runtime_level", 0) >= 2:
        test = poc.get("test_file_path", "unknown test")
        return "✅", f"proved at level {poc['runtime_level']} — {test}"
    lvl = poc.get("runtime_level", 0)
    status = poc.get("status", "missing")
    return "❌", f"not proved (level={lvl}, status={status})"


def check_q2(poc: dict) -> tuple[str, str]:
    """Q2: Level 3 proved?"""
    if poc.get("status") == "proved" and poc.get("runtime_level", 0) >= 3:
        test = poc.get("test_file_path", "unknown test")
        return "✅", f"proved at level {poc['runtime_level']} — {test}"
    lvl = poc.get("runtime_level", 0)
    status = poc.get("status", "missing")
    if lvl == 2 and status == "proved":
        return "⚠️", "level 2 proved but level 3 not yet attempted"
    return "❌", f"not proved (level={lvl}, status={status})"


def check_q3(judge: dict, triage: dict) -> tuple[str, str]:
    """Q3: Direct loss?"""
    # Try judge simulation first
    if judge:
        reasoning = judge.get("reasoning", "")
        loss_keywords = [
            "fund theft", "direct loss", "collateral", "steal", "drain",
            "bad debt", "liquidat", "insolvent", "permanent", "blocking",
        ]
        if any(k in reasoning.lower() for k in loss_keywords):
            sev = judge.get("simulated_severity", "?")
            if sev in ("high", "critical"):
                return "✅", f"judge assessed {sev} with direct-loss reasoning"
            return "⚠️", f"judge assessed {sev} — verify loss is direct"
    # Fall back to triage
    if triage:
        impact = triage.get("impact", {})
        loss_type = impact.get("loss_type", "none")
        if loss_type not in ("none", "unknown", ""):
            return "⚠️", f"triage loss_type={loss_type} — verify directness"
        sev = triage.get("recommended_severity", "?")
        if sev in ("high", "critical"):
            return "⚠️", "high severity but loss_type not classified — check manually"
    return "❓", "could not auto-determine — check judge_simulation reasoning"


def check_q4(exploit: dict) -> tuple[str, str]:
    """Q4: Permissionless?"""
    if not exploit:
        return "❓", "no exploitability data — run model_exploitability.py first"
    perms = exploit.get("required_permissions", [])
    preconds = exploit.get("required_preconditions", [])
    blocked = exploit.get("blocked_by_auth", False)
    if blocked:
        return "❌", "blocked_by_auth=true — requires privileged access"
    if not perms and not preconds:
        return "✅", "no permissions or preconditions required"
    conds = perms + preconds
    return "⚠️", f"requires: {', '.join(conds[:3])}"


def check_q5(triage: dict, judge: dict) -> tuple[str, str]:
    """Q5: Victim condition realistic?"""
    if judge:
        objections = judge.get("objections", [])
        for obj in objections:
            if "victim" in obj.lower() or "allowance" in obj.lower() or "unusual" in obj.lower():
                return "⚠️", f"judge objection: {obj[:80]}"
    if triage:
        impact = triage.get("impact", {})
        realistic = triage.get("attacker_model", {}).get("realistic", None)
        if realistic is False:
            return "⚠️", "triage attacker_model.realistic=false — review preconditions"
        if realistic is True:
            return "✅", "triage attacker_model.realistic=true"
    return "❓", "could not auto-determine — check triage impact and preconditions"


def check_q6(dupes: dict, finding_id: str) -> tuple[str, str]:
    """Q6: Likely duplicate?"""
    if not dupes:
        return "❓", "no duplicate risk data — run estimate_duplicate_risk.py first"
    risk = dupes.get("duplicate_probability", 0)
    similar = dupes.get("similar_findings", [])
    if risk > 0.6:
        return "⚠️", f"duplicate probability={risk:.0%} — merge root causes before submitting"
    if risk > 0.3:
        return "⚠️", f"moderate duplicate risk={risk:.0%} — check {similar[:2]}"
    return "✅", f"low duplicate risk={risk:.0%}" if risk else "❓ no risk score computed"


def check_q7(finding_id: str) -> tuple[str, str]:
    """Q7: One-sentence impact? — checks submission file for a crisp sentence."""
    sub_path = audit_path("output/submissions") / f"{finding_id}_submission.md"
    if not sub_path.exists():
        return "❓", "no submission file found — write submission first"
    text = sub_path.read_text()
    # Look for a summary section — first paragraph after ## Summary
    lines = text.split("\n")
    in_summary = False
    summary_lines = []
    for line in lines:
        if line.startswith("## Summary"):
            in_summary = True
            continue
        if in_summary:
            if line.startswith("##"):
                break
            if line.strip():
                summary_lines.append(line.strip())
    if summary_lines:
        first_sentence = summary_lines[0]
        if len(first_sentence) > 20 and len(first_sentence) < 300:
            return "✅", f'summary starts: "{first_sentence[:100]}..."'
        if len(first_sentence) >= 300:
            return "⚠️", "summary first line is very long — consider tightening"
    return "❓", "submission exists but could not extract a clear one-sentence summary"


def evaluate_finding(finding_id: str, all_data: dict) -> dict:
    poc      = all_data["poc"].get(finding_id, {})
    judge    = all_data["judge"].get(finding_id, {})
    triage   = all_data["triage"].get(finding_id, {})
    exploit  = all_data["exploit"].get(finding_id, {})
    dupes    = all_data["dupes"].get(finding_id, {})

    q1_sym, q1_txt = check_q1(poc)
    q2_sym, q2_txt = check_q2(poc)
    q3_sym, q3_txt = check_q3(judge, triage)
    q4_sym, q4_txt = check_q4(exploit)
    q5_sym, q5_txt = check_q5(triage, judge)
    q6_sym, q6_txt = check_q6(dupes, finding_id)
    q7_sym, q7_txt = check_q7(finding_id)

    all_green = all(
        s in ("✅",) for s in [q1_sym, q2_sym, q3_sym, q4_sym, q5_sym, q7_sym]
    )
    any_red = any(
        s == "❌" for s in [q1_sym, q2_sym, q3_sym, q4_sym, q5_sym, q6_sym, q7_sym]
    )

    if any_red:
        overall = "block"
    elif all_green:
        overall = "ready"
    else:
        overall = "conditional"

    return {
        "finding_id": finding_id,
        "overall": overall,
        "checklist": {
            "q1_level2_proved":       {"symbol": q1_sym, "detail": q1_txt},
            "q2_level3_proved":       {"symbol": q2_sym, "detail": q2_txt},
            "q3_direct_loss":         {"symbol": q3_sym, "detail": q3_txt},
            "q4_permissionless":      {"symbol": q4_sym, "detail": q4_txt},
            "q5_victim_realistic":    {"symbol": q5_sym, "detail": q5_txt},
            "q6_likely_duplicate":    {"symbol": q6_sym, "detail": q6_txt},
            "q7_one_sentence_impact": {"symbol": q7_sym, "detail": q7_txt},
        },
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def print_report(results: list[dict]):
    labels = [
        "L2?", "L3?", "Direct loss?", "Permissionless?",
        "Victim realistic?", "Likely dup?", "1-sentence?",
    ]
    q_keys = [
        "q1_level2_proved", "q2_level3_proved", "q3_direct_loss",
        "q4_permissionless", "q5_victim_realistic", "q6_likely_duplicate",
        "q7_one_sentence_impact",
    ]

    header = f"{'Finding':<10} {'Overall':<12} " + " ".join(f"{l:<15}" for l in labels)
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    for r in results:
        fid = r["finding_id"]
        overall = r["overall"].upper()
        syms = [r["checklist"][k]["symbol"] for k in q_keys]
        row = f"{fid:<10} {overall:<12} " + " ".join(f"{s:<15}" for s in syms)
        print(row)
    print("=" * len(header))


def main():
    parser = argparse.ArgumentParser(description="Run 7-question quality checklist")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--finding-id", help="Single finding ID")
    group.add_argument("--all", action="store_true", help="All proved findings")
    parser.add_argument("--report", action="store_true", help="Print summary table")
    args = parser.parse_args()

    # Load all pipeline data
    triage_combined = {}
    triage_combined.update(load_jsonl("data/triage/submit.jsonl"))
    triage_combined.update(load_jsonl("data/triage/poc_required.jsonl"))

    all_data = {
        "poc":     load_jsonl("data/runtime_poc/results.jsonl"),
        "judge":   load_jsonl("data/judge_simulation/results.jsonl"),
        "triage":  triage_combined,
        "exploit": load_jsonl("data/exploitability/models.jsonl"),
        "dupes":   load_jsonl("data/duplicates/risk.jsonl"),
    }

    # Determine which findings to process
    if args.all:
        finding_ids = sorted(all_data["poc"].keys())
    else:
        finding_ids = [args.finding_id]

    if not finding_ids:
        print("No findings found in runtime_poc/results.jsonl", file=sys.stderr)
        sys.exit(1)

    # Evaluate
    results = [evaluate_finding(fid, all_data) for fid in finding_ids]

    # Write output
    out_dir = audit_path("data/quality_checklist")
    out_path = out_dir / "results.jsonl"

    # Load existing, replace entries for evaluated findings
    existing = {}
    if out_path.exists():
        with open(out_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    d = json.loads(line)
                    existing[d["finding_id"]] = d
    for r in results:
        existing[r["finding_id"]] = r
    with open(out_path, "w") as f:
        for d in existing.values():
            f.write(json.dumps(d) + "\n")

    if args.report or args.all:
        print_report(results)

    print(f"\nWritten → {out_path}")

    # Print per-finding detail
    for r in results:
        fid = r["finding_id"]
        overall = r["overall"].upper()
        print(f"\n  {fid}: {overall}")
        for key, val in r["checklist"].items():
            label = key.replace("_", " ").upper()
            print(f"    {val['symbol']}  {label}: {val['detail']}")

    import subprocess as _sp
    _sp.run([sys.executable, str(Path(__file__).resolve().parent / "generate_status.py")],
            check=False, capture_output=True)
    # Exit non-zero if any finding is blocked
    if any(r["overall"] == "block" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
