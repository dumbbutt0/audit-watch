"""P222 — Human-review priority lane (research-only, display/prioritization only).

A pure, side-effect-free classifier that decides *which not-auto-reportable candidates a human should
adjudicate first*. It is a SEPARATE namespace from severity:

  * It reads ONLY display/evidence fields: l3_status, impact_type, reachability_class, conversion_outcome /
    mechanism_confirmed, dependency_mocks, and refutation notes.
  * It writes ONLY the six priority fields below.
  * It NEVER reads or writes attacker_model, any severity field, submission_ready, routing_allowed, or
    high_promotion_allowed. decide() (scripts/validate_p208_l3_readiness.py) is the sole severity authority
    and keys off attacker_model — never off anything this module produces.

Model + rules: documentation/research/assisted_mode/p222_human_review_priority/{HUMAN_REVIEW_PRIORITY_MODEL,
REACHABILITY_CLASS_MODEL,PRIORITY_RULES}.md.

Output keys: human_review_priority, human_review_reason_codes, reachability_class, priority_explanation,
priority_blockers, should_surface_above_noise.
"""
from __future__ import annotations

from typing import Any, Dict, List

# ---- priority values (display only; NOT severity, NOT submission) ----
PRIORITY_VALUES = ("NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL_HUMAN_REVIEW")

# impact classifications (over an already-PROVEN impact) that qualify a candidate for the lane
QUALIFYING_IMPACT = {
    "core_safety_control_bypass",
    "emergency_pause_bypass",
    "core_entry_exit_dos",
    "cross_chain_message_invariant_bypass",
    "protocol_accounting_invariant_violation",
    "fund_lock_or_failed_refund",
}
_SAFETY_CONTROL_IMPACT = {"core_safety_control_bypass", "emergency_pause_bypass"}
_DOS_IMPACT = {"core_entry_exit_dos"}
_FUND_IMPACT = {"fund_lock_or_failed_refund"}

# reachability classes that make a candidate NOT auto-reportable but still worth a human threat-model call
QUALIFYING_REACH = {
    "TRUSTED_SYSTEM_ACTOR_REACHABLE",
    "PROGRAM_ACCEPTED_ACTOR_REACHABLE",
    "KEEPER_OR_RELAYER_REACHABLE",
    "ADMIN_OR_OWNER_REACHABLE",
    "PRIVILEGED_ONLY_REACHABLE",
}
# trusted-system / privileged actor bands (drive the trusted-system reason codes)
_TRUSTED_SYSTEM_REACH = {"TRUSTED_SYSTEM_ACTOR_REACHABLE", "KEEPER_OR_RELAYER_REACHABLE"}
# reachability that is auto-reportable through the normal path -> never enters the lane
_AUTO_REPORTABLE_REACH = {"UNPRIVILEGED_REACHABLE"}
# reachability that is real-but-impact-unproven candidates can still leave a residual
_REAL_PATH_REACH = {
    "UNPRIVILEGED_REACHABLE",
    "PROGRAM_ACCEPTED_ACTOR_REACHABLE",
    "TRUSTED_SYSTEM_ACTOR_REACHABLE",
    "KEEPER_OR_RELAYER_REACHABLE",
    "ADMIN_OR_OWNER_REACHABLE",
    "PRIVILEGED_ONLY_REACHABLE",
}

_CONVERSION_HIT = {"CLEAN_HIT", "STRONG_PARTIAL"}


def _s(v: Any) -> str:
    return str(v).strip() if v is not None else ""


def _get(record: Dict[str, Any], *keys: str) -> Any:
    """First present value among keys, tolerating a nested 'l3' dict (synced-record shape)."""
    for k in keys:
        if record.get(k) not in (None, ""):
            return record.get(k)
    l3 = record.get("l3")
    if isinstance(l3, dict):
        for k in keys:
            if l3.get(k) not in (None, ""):
                return l3.get(k)
    return None


def evaluate_priority(record: Dict[str, Any]) -> Dict[str, Any]:
    """Pure classifier. `record` is a candidate bundle or synced finding; returns the six priority fields.

    Defaults: human_review_priority=NONE, reachability_class=REACHABILITY_UNKNOWN,
    should_surface_above_noise=False. Severity / submission flags are never touched.
    """
    l3_status = _s(_get(record, "l3_status")).upper()
    impact_type = _s(_get(record, "impact_type")).lower()
    reach = _s(_get(record, "reachability_class")) or "REACHABILITY_UNKNOWN"
    conversion = _s(_get(record, "conversion_outcome", "conversion", "conversion_classification")).upper()
    mechanism_confirmed = bool(record.get("mechanism_confirmed"))
    dependency_mocks = _s(_get(record, "dependency_mocks", "corrected_reference_type")).lower()
    notes = (_s(_get(record, "source_validity_notes", "limitations")) + " " + _s(record.get("scoring_note"))).lower()
    blocker = _s(_get(record, "high_promotion_blocker", "blocker_reason", "main_blocker"))

    refuted = (l3_status == "FAIL") or (reach == "SOURCE_REFUTED") or ("refut" in notes)
    mock_created = dependency_mocks == "creates_vulnerable_condition"
    cond_mechanism = mechanism_confirmed or (conversion in _CONVERSION_HIT)
    qual_impact = impact_type in QUALIFYING_IMPACT
    qual_reach = reach in QUALIFYING_REACH
    in_lane_reach = reach not in _AUTO_REPORTABLE_REACH and reach != "SELF_INFLICTED_ONLY"

    priority = "NONE"
    reasons: List[str] = []
    blockers: List[str] = []
    explanation = "no human-review prioritization signal"

    if refuted or mock_created:
        # impact disproven (or only the mock created it): never HIGH/MEDIUM. A real-but-unproven path may
        # leave a low residual; a source-refuted / unknown path is just NONE.
        if mock_created:
            priority, explanation = "NONE", "impact exists only under a vulnerability-creating mock; not a finding"
        elif reach == "SOURCE_REFUTED":
            priority, explanation = "NONE", "source-refuted; nothing for a human to prioritize"
        elif reach in _REAL_PATH_REACH:
            priority = "LOW"
            reasons = ["LOW_CONFIDENCE_NOISE"]
            explanation = "impact refuted by L3; a real but minor code-quality residual remains"
        else:
            priority, explanation = "NONE", "impact refuted and no reachable residual"
    elif l3_status == "PASS" and qual_impact and in_lane_reach:
        if cond_mechanism and qual_reach:
            # the trusted-system lane: L3-proven core impact, not auto-reportable only because a
            # program-specific threat-model decision is required.
            priority = "CRITICAL_HUMAN_REVIEW" if impact_type in _FUND_IMPACT else "HIGH"
            reasons = ["PROGRAM_THREAT_MODEL_DECISION_REQUIRED"]
            if impact_type in _SAFETY_CONTROL_IMPACT:
                reasons.append("CORE_SAFETY_CONTROL_BYPASS")
            reasons.append("L3_PASS_BUT_PRIVILEGED_TRIGGER")
            if reach in _TRUSTED_SYSTEM_REACH:
                reasons.append("TRUSTED_SYSTEM_ACTOR_REACHABLE")
            explanation = ("L3 PASS on a core safety/control path reachable by a trusted-system / privileged "
                           "actor; not auto-reportable — a program threat-model decision is required")
        else:
            # L3-proven core impact but the HIGH bar is not met (reachability unknown, or a wrong-mechanism /
            # scope-dependent partial): a human must make a scope / program-rule call.
            priority = "MEDIUM"
            reasons = ["L3_PASS_BUT_SCOPE_DECISION_REQUIRED", "NEEDS_PROGRAM_RULE_INTERPRETATION"]
            if impact_type in _DOS_IMPACT:
                reasons.append("NEEDS_SEVERITY_POLICY_DECISION")
            explanation = ("L3 PASS on a qualifying impact, but reachability/scope is undetermined or the "
                           "mechanism is a partial match; needs a human scope decision")
    else:
        priority, explanation = "NONE", "not L3-proven on a qualifying core-impact + non-unprivileged path"

    if priority in ("HIGH", "MEDIUM", "CRITICAL_HUMAN_REVIEW") and blocker:
        blockers = [blocker]

    return {
        "human_review_priority": priority,
        "human_review_reason_codes": reasons,
        "reachability_class": reach,
        "priority_explanation": explanation,
        "priority_blockers": blockers,
        "should_surface_above_noise": priority in ("MEDIUM", "HIGH", "CRITICAL_HUMAN_REVIEW"),
    }
