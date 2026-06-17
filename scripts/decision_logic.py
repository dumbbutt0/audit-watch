#!/usr/bin/env python3
"""
decision_logic.py — Single source of truth for pipeline decision logic.

Consumed by:
  - run_specialist_review.py  (per-finding action: SUBMIT/REVISE/POC_FIRST/MERGE/DROP)
  - dashboard.py              (/api/status/summary layer computation)
  - generate_status.py        (phone /status command — imports compute_pipeline_layer)

Public API
----------
compute_finding_action(exploit_score, dup_risk, cal_sev, poc_level, judge_outcome) -> str
    Returns one of: SUBMIT | REVISE | POC_FIRST | MERGE | DROP

compute_pipeline_layer(flags) -> tuple[int, str, str, str]
    Returns (layer, last_completed, next_action, next_command).
    `flags` is a dict with boolean/count keys — see docstring.
"""

from __future__ import annotations

SEV_ORDER: dict[str, int] = {
    "critical": 0, "high": 1, "medium": 2, "low": 3, "qa": 4, "invalid": 5, "?": 9,
}

LAYER_LABELS: list[str] = [
    "Not started",
    "Static Analysis",
    "Agent Discovery",
    "Report Generation",
    "Triage",
    "Specialist Review",
    "PoC",
    "Quality Checklist",
    "Completeness Gate",
    "Final Submission",
]


def compute_finding_action(
    exploit_score: int,
    dup_risk: str,
    cal_sev: str,
    poc_level: int,
    judge_outcome: str,
) -> str:
    """
    Compute the recommended next action for a single finding.

    Returns one of: SUBMIT | REVISE | POC_FIRST | MERGE | DROP
    """
    # DROP conditions
    if exploit_score < 3:
        return "DROP"
    if judge_outcome == "rejected":
        return "DROP"
    if dup_risk == "high":
        return "MERGE"

    # POC_FIRST
    if poc_level == 0 and exploit_score >= 3 and judge_outcome == "needs_poc":
        return "POC_FIRST"

    # SUBMIT
    if (
        exploit_score >= 4
        and dup_risk != "high"
        and SEV_ORDER.get(cal_sev, 9) <= SEV_ORDER.get("medium", 9)
        and judge_outcome in ("accepted", "accepted_downgraded")
        and poc_level >= 1
    ):
        return "SUBMIT"

    # REVISE
    if judge_outcome == "accepted_downgraded":
        return "REVISE"

    # Fallback
    if poc_level == 0 and exploit_score >= 3:
        return "POC_FIRST"

    return "REVISE"


def compute_pipeline_layer(flags: dict) -> tuple[int, str, str, str]:
    """
    Determine the current pipeline layer and next recommended action.

    Parameters (all optional, default to falsy)
    ------------------------------------------
    static_done          bool   — static.json exists
    findings_done        bool   — at least one findings_*.json exists
    merged_done          bool   — merged_findings.json exists
    triage_submit        int    — count of submit findings
    triage_poc           int    — count of poc_required findings
    triage_down          int    — count of downgraded findings
    triage_rej           int    — count of rejected findings
    specialist_done      int    — count of specialist-reviewed findings
    specialist_total     int    — total findings count
    poc_proved           int    — count of proved PoCs
    poc_failed           int    — count of failed PoCs
    poc_pending          int    — count of pending PoCs
    checklist_passed     int    — checklist passed count
    checklist_total      int    — checklist total count
    completeness_done    int    — completeness gate findings assessed
    submission_ready     int    — count of submission-ready findings
    blockers             int    — count of blocking issues

    Returns
    -------
    (layer, last_completed, next_action, next_command)
    """
    g = flags.get

    layer = 0
    last_completed = "Nothing yet"
    next_action = "Run static analysis"
    next_command = "python tools/static_analysis.py <contract_path>"

    if g("static_done"):
        layer = 1
        last_completed = "Static analysis complete"
        next_action = "Run specialist agents"
        next_command = "(spawn agents via Task tool)"

    if g("findings_done") or g("merged_done"):
        layer = 2
        last_completed = "Agent discovery complete"
        next_action = "Run report generator"
        next_command = "python tools/report_generator.py"

    if g("merged_done"):
        layer = 3
        last_completed = "Report generated"
        next_action = "Run triage"
        next_command = "python scripts/triage_findings.py"

    triage_any = g("triage_submit", 0) + g("triage_poc", 0) + g("triage_down", 0) + g("triage_rej", 0)
    if triage_any > 0:
        layer = 4
        total_t = triage_any
        last_completed = (
            f"Triage complete ({g('triage_submit', 0)} submit, "
            f"{g('triage_poc', 0)} poc_required, "
            f"{g('triage_down', 0) + g('triage_rej', 0)} filtered)"
        )
        next_action = "Run specialist review"
        next_command = "python scripts/run_specialist_review.py"

    specialist_done = g("specialist_done", 0)
    if specialist_done > 0:
        total = g("specialist_total", specialist_done)
        layer = 5
        last_completed = f"Specialist review: {specialist_done}/{total} findings scored"
        next_action = "Run PoC generation for poc_required findings"
        next_command = "python scripts/run_integrated_poc.py --all"

    poc_total = g("poc_proved", 0) + g("poc_failed", 0) + g("poc_pending", 0)
    if poc_total > 0:
        layer = 6
        last_completed = f"{g('poc_proved', 0)}/{poc_total} PoC tests passing"
        next_action = "Run quality checklist"
        next_command = "python scripts/run_quality_checklist.py --all"

    checklist_total = g("checklist_total", 0)
    if checklist_total > 0:
        layer = 7
        last_completed = f"Quality checklist: {g('checklist_passed', 0)}/{checklist_total} passed"
        next_action = "Run PoC completeness gate"
        next_command = "python scripts/analyze_poc_completeness.py --all"

    completeness_done = g("completeness_done", 0)
    if completeness_done > 0:
        layer = 8
        last_completed = f"Completeness gate: {completeness_done} findings assessed"
        next_action = "Build final submission pack"
        next_command = "python scripts/final_submission_pack.py"

    submission_ready = g("submission_ready", 0)
    blockers = g("blockers", 0)
    if submission_ready > 0 and blockers == 0:
        layer = 9
        last_completed = f"Submission pack ready ({submission_ready} findings)"
        next_action = "Review and submit"
        next_command = "# Review output/submission_pack.md then submit"

    return layer, last_completed, next_action, next_command


def layer_label(layer: int) -> str:
    return LAYER_LABELS[min(layer, len(LAYER_LABELS) - 1)]
