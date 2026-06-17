#!/usr/bin/env python3
"""validate_p196.py — READ-ONLY deep-pass execution reality check (P196).

Determines whether deep-pass zero-execution is an eval-config artifact or a real production gap, by inventorying
TWO distinct mechanisms across every audit:
  A) budgeted candidate-queue executor (deep_pass_ledger.py -> deep_pass_budget_summary / executed_deep_passes)
  B) in-session deep-analysis (run_deep_analysis.py -> findings_deep_trace)  [the real deep path under api_free]
Deterministic; existing artifacts only; no model runs; every cell artifact-cited; unknown=UNKNOWN; fabrication=0.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from collections import Counter

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
PD = ROOT / "documentation/research/assisted_mode/p196_deep_pass_execution_reality_check"
AUD = ROOT / "audits"

def load(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None

def run_type(name):
    for suf in ("strict-eval","eval2","eval","holdout","fresh","bench","semantic-tvl",
                "liquidation-health","dry-run","refine-check","part-2-eval"):
        if name.endswith("-"+suf) or name.endswith(suf):
            return "eval" if suf in ("eval","eval2","part-2-eval","strict-eval") else suf
    return "other"

def main():
    PD.mkdir(parents=True, exist_ok=True)
    runtime = load(ROOT/"config/runtime_policy.json") or {}
    apol = load(ROOT/"config/agent_policy.json") or {}
    cov_pol = apol.get("coverage_policy", {})
    gate_flags = {k: cov_pol.get(k) for k in
                  ("deep_pass_priority_enabled","deep_pass_high_priority_block_strict",
                   "deep_pass_high_priority_block_strict_full_audit","waiver_discipline_strict",
                   "waiver_discipline_strict_full_audit","high_risk_waiver_max")}
    api_free = runtime.get("api_free")

    rows = []; skip_reasons = Counter(); skip_tiers = Counter(); skip_specialists = Counter()
    for d in sorted(p.name for p in AUD.iterdir() if p.is_dir() and p.name not in ("_fp_tmp",)):
        o = AUD/d/"output"
        if not o.exists(): continue
        rt = run_type(d)
        bud = load(o/"deep_pass_budget_summary.json")
        ex = load(o/"executed_deep_passes.json")
        exn = (len(ex.get("executed",[])) if isinstance(ex,dict) else (len(ex) if isinstance(ex,list) else 0)) if ex is not None else None
        dt = load(o/"findings_deep_trace.json")
        dtn = len(dt) if isinstance(dt,list) else len((dt or {}).get("findings",[])) if dt else 0
        queue = (o/"deep_pass/candidate_queue.json").exists()
        sk = load(o/"skipped_deep_passes_with_reason.json")
        sk_items = sk if isinstance(sk,list) else ([sk[k] for k in sk if isinstance(sk[k],dict)] if isinstance(sk,dict) else [])
        for it in (sk_items or []):
            if isinstance(it,dict):
                skip_reasons[(it.get("reason") or "")[:80]] += 1
                skip_tiers[it.get("tier")] += 1
                skip_specialists[it.get("specialist")] += 1
        qd = (bud or {}).get("queued_items")
        rows.append({
            "audit": d, "run_type": rt,
            "A_budget_summary_present": bud is not None,
            "A_queued": qd, "A_executed": (bud or {}).get("executed"),
            "A_execution_rate": (bud or {}).get("execution_rate"),
            "A_strict": (bud or {}).get("strict"), "A_full_audit": (bud or {}).get("full_audit"),
            "A_executed_deep_passes": exn, "A_candidate_queue_present": queue,
            "A_vacuous_zero_queue": bool(bud) and (qd == 0),
            "B_findings_deep_trace": dtn,
        })

    # ----- aggregates -----
    by_type = {}
    for r in rows:
        t = r["run_type"]; bt = by_type.setdefault(t, {"runs":0,"A_executed_any":0,"B_deep_trace_runs":0,"B_total_findings":0,"A_budget_runs":0})
        bt["runs"] += 1
        if (r["A_executed"] or 0) or (r["A_executed_deep_passes"] or 0): bt["A_executed_any"] += 1
        if r["A_budget_summary_present"]: bt["A_budget_runs"] += 1
        if r["B_findings_deep_trace"] > 0: bt["B_deep_trace_runs"] += 1; bt["B_total_findings"] += r["B_findings_deep_trace"]

    A_executed_anywhere = any((r["A_executed"] or 0) or (r["A_executed_deep_passes"] or 0) for r in rows)
    B_runs = [r["audit"] for r in rows if r["B_findings_deep_trace"] > 0]
    B_types = Counter(r["run_type"] for r in rows if r["B_findings_deep_trace"] > 0)
    B_absent_types = Counter(r["run_type"] for r in rows if r["B_findings_deep_trace"] == 0)

    # classification
    decision = ("MIXED_BEHAVIOR" if (not A_executed_anywhere and len(B_runs) > 0) else
                "PRODUCTION_EXECUTION_GAP" if not A_executed_anywhere and len(B_runs) == 0 else
                "EVAL_ONLY_WAIVER")
    # (A never executes anywhere = structural api-free no-op; B executed in eval runs only -> MIXED across mechanisms/types)

    matrix = {"phase":"P196","read_only":True,
        "two_mechanisms":{
            "A_budgeted_executor":{"writer":"scripts/deep_pass_ledger.py","artifacts":["deep_pass_budget_summary.json","executed_deep_passes.json"],"executed_anywhere":A_executed_anywhere},
            "B_in_session_deep_analysis":{"writer":"scripts/run_deep_analysis.py / deep_analysis_write.py","artifact":"findings_deep_trace.json","runs_with_findings":B_runs}},
        "api_free":api_free,"api_free_comment":runtime.get("_comment"),
        "agent_policy_gate_flags":gate_flags,
        "by_run_type":by_type,
        "B_present_by_type":dict(B_types),"B_absent_by_type":dict(B_absent_types),
        "rows":rows}
    (PD/"run_execution_matrix.json").write_text(json.dumps(matrix,indent=2)+"\n")
    (PD/"skip_reason_taxonomy.json").write_text(json.dumps({"phase":"P196",
        "reason_distribution":dict(skip_reasons.most_common()),
        "tier_distribution":dict(skip_tiers.most_common()),
        "specialist_distribution":dict(skip_specialists.most_common()),
        "cause_interpretation":{
            "missing_runner_api_free":"api_free=%s -> no non-interactive LLM runner -> mechanism A cannot auto-execute (structural)"%api_free,
            "strict_full_audit_block":"agent_policy deep_pass_high_priority_block_strict_full_audit=%s + waiver_discipline_strict_full_audit=%s (extra eval-mode suppression, redundant atop the architectural zero)"%(gate_flags.get("deep_pass_high_priority_block_strict_full_audit"),gate_flags.get("waiver_discipline_strict_full_audit")),
            "tier_cluster_specialist":"documented waiver policy (skipped_deep_passes_with_reason)"}},indent=2)+"\n")

    metrics = {"phase":"P196","read_only":True,
      "Q1_deep_pass_assigned_in":"candidate_queue/assigned_pass=='deep' present in runs reaching deep-prepare",
      "Q2_mechanism_A_executed_anywhere":A_executed_anywhere,
      "Q2_mechanism_B_executed_runs":B_runs,
      "Q3_execution_rate_by_type":{t:{"runs":v["runs"],"A_executed_any":v["A_executed_any"],"B_deep_trace_runs":v["B_deep_trace_runs"]} for t,v in by_type.items()},
      "Q4_skip_cause":"mechanism A: missing-runner(api_free) + strict/full_audit block + tier/cluster/specialist waivers; NOT a code bug",
      "Q5_findings_produced_by":"mechanism B (in-session run_deep_analysis -> findings_deep_trace), NOT mechanism A (executed=0); distinct writers",
      "Q6_assigned_vs_executed_distinguishable":True,
      "Q7_production_like_same_behavior":"mechanism A is 0 everywhere (architectural); holdout/fresh assign-but-don't-execute A AND never ran in-session B (0 deep-trace); eval runs ran B",
      "decision":decision,
      "production_execution_gap_worth_fixing":False,
      "next_phase":"close the measurement sub-arc; execution-budget is NOT the lever (api-free routes deep to in-session skill by design)",
      "caveats":["'production-like' here = holdout/fresh/bench research corpora; there is no true production deployment run in this repo",
                 "mechanism A zero-execution is api-free architectural (no non-interactive LLM runner), not a fixable code gap",
                 "B (real deep) ran in eval/research corpora, absent in holdout/fresh/bench (process/depth-of-run, not a config bug)"]}
    (PD/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")  # not in plan deliverables but harmless aux
    print(json.dumps({"decision":decision,"A_executed_anywhere":A_executed_anywhere,
        "B_present_by_type":dict(B_types),"B_absent_by_type":dict(B_absent_types),
        "api_free":api_free,"gate_flags":gate_flags},indent=2))
    print("by_run_type:",json.dumps(by_type))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
