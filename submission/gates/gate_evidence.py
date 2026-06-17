#!/usr/bin/env python3
"""
gate_evidence.py — Gate 6: Evidence completeness.

Requires (non-empty):
  - code lines (evidence_links)
  - affected functions
  - call trace
  - state transition
  - logs or test output / proof artifact path

The set of always-required-non-empty fields is shared with the schema via
x_gate_required_nonempty. State transition and proof artifact are checked
explicitly here too. Missing evidence is a proof deficiency -> NEEDS_PROOF.
"""
from __future__ import annotations

from _common import NEEDS_PROOF, PASS, GateResult, is_empty, required_nonempty_fields

GATE = 6
NAME = "evidence_completeness"

_FIELD_LABELS = {
    "root_cause": "root cause",
    "affected_contracts": "affected contracts",
    "affected_functions": "affected functions",
    "call_trace": "call trace",
    "evidence_links": "code lines / evidence links",
}


def evaluate(candidate: dict) -> list[GateResult]:
    missing: list[str] = []

    for field in required_nonempty_fields():
        if is_empty(candidate.get(field)):
            missing.append(_FIELD_LABELS.get(field, field))

    if is_empty(candidate.get("state_transition")):
        missing.append("state transition")

    # logs / test output / proof artifact path
    if is_empty(candidate.get("poc_path")) and is_empty(candidate.get("evidence_links")):
        missing.append("logs/test output or proof artifact path")

    if missing:
        # de-duplicate while preserving order
        seen: list[str] = []
        for m in missing:
            if m not in seen:
                seen.append(m)
        return [GateResult(
            GATE, NAME, NEEDS_PROOF,
            "Evidence is incomplete; supply: " + "; ".join(seen),
            tag="evidence_incomplete",
            detail={"missing": seen},
        )]

    return [GateResult(
        GATE, NAME, PASS,
        "Code lines, affected functions, call trace, state transition and proof "
        "artifact are all present.",
    )]
