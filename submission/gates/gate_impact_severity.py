#!/usr/bin/env python3
"""
gate_impact_severity.py — Gate 3: Impact / severity.

Requires:
  - a concrete impact (impact_category that is not 'info', plus a quantified
    asset_delta or named state transition)
  - severity mapped to the bounty program's impact table
  - NO severity inflation: the claimed severity may not exceed the ceiling the
    impact + proof can support
  - worst-case and realistic-case impact separated

Severity inflation -> FAIL (DO_NOT_SUBMIT) with an explicit downgrade note
naming the supportable severity, so a human can re-file at the correct level.
"""
from __future__ import annotations

from _common import (
    FAIL,
    IMPACT_SEVERITY_CEILING,
    PASS,
    SEVERITY_RANK,
    WARN,
    GateResult,
    is_empty,
)

GATE = 3
NAME = "impact_severity"


def evaluate(candidate: dict) -> list[GateResult]:
    results: list[GateResult] = []

    impact_cat = candidate.get("impact_category", "")
    claim = candidate.get("severity_claim", "")
    asset_delta = candidate.get("asset_delta")
    state_transition = candidate.get("state_transition")
    proof_type = candidate.get("proof_type", "")
    poc_status = candidate.get("poc_status", "")

    # concrete impact required (unless the claim itself is Informational)
    concrete = not (is_empty(asset_delta) and is_empty(state_transition))
    if impact_cat in ("", "info") and claim not in ("Informational", "Low"):
        results.append(GateResult(
            GATE, NAME, FAIL,
            f"Severity '{claim}' claimed but impact_category is "
            f"'{impact_cat or 'unset'}' (no concrete security/economic impact).",
            tag="no_concrete_impact",
        ))
    elif not concrete and claim in ("Critical", "High"):
        results.append(GateResult(
            GATE, NAME, FAIL,
            f"Severity '{claim}' claimed but no concrete impact is quantified "
            "(asset_delta and state_transition are both empty).",
            tag="no_concrete_impact",
        ))

    # severity ceiling from impact category, optionally lifted by a real PoC
    ceiling = _supportable_ceiling(impact_cat, asset_delta, proof_type, poc_status)
    if claim and ceiling and SEVERITY_RANK.get(claim, 0) > SEVERITY_RANK.get(ceiling, 0):
        results.append(GateResult(
            GATE, NAME, FAIL,
            f"Severity inflation: claims '{claim}' but proven impact supports at "
            f"most '{ceiling}'. Re-file as '{ceiling}'.",
            tag="severity_inflated",
            detail={"claimed": claim, "supportable": ceiling,
                    "downgrade_note": f"Recommended severity: {ceiling}"},
        ))

    # mapping to the program's impact table
    mapping = candidate.get("bounty_program_mapping") or {}
    just = candidate.get("severity_justification") or {}
    table_ref = just.get("program_table_mapping") or mapping.get("scope_reference")
    if is_empty(table_ref):
        results.append(GateResult(
            GATE, NAME, WARN,
            "Severity is not mapped to the program's impact table "
            "(severity_justification.program_table_mapping is empty).",
            tag="unmapped_severity",
        ))

    # worst-case vs realistic-case separation
    if is_empty(just.get("worst_case")) or is_empty(just.get("realistic_case")):
        results.append(GateResult(
            GATE, NAME, WARN,
            "Worst-case and realistic-case impact are not both stated in "
            "severity_justification.",
            tag="cases_not_separated",
        ))

    if not results:
        results.append(GateResult(
            GATE, NAME, PASS,
            "Concrete impact present, severity within supportable ceiling, mapped "
            "to the program table, worst/realistic cases separated.",
        ))
    return results


def _supportable_ceiling(impact_cat: str, asset_delta, proof_type: str, poc_status: str) -> str:
    """Severity ceiling for an impact category, lifted one notch when a runnable,
    passing PoC with a quantified asset_delta backs it."""
    base = IMPACT_SEVERITY_CEILING.get(impact_cat, "Informational")
    has_strong_poc = (
        proof_type == "runnable_poc"
        and poc_status == "passing"
        and not is_empty(asset_delta)
    )
    if not has_strong_poc:
        return base
    # lift by one notch, capped at Critical
    order = ["Informational", "Low", "Medium", "High", "Critical"]
    idx = min(order.index(base) + 1, len(order) - 1)
    return order[idx]
