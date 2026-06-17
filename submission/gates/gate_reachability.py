#!/usr/bin/env python3
"""
gate_reachability.py — Gate 2: Attacker reachability.

Requires, for an unprivileged attacker:
  - an external attacker entrypoint
  - no privileged role (unless allowed; the scope gate owns the hard block on
    privilege, this gate only NEEDS_PROOF when the path is under-specified)
  - the exact call path
  - preconditions
  - state setup
  - the reason defenses do not block the path

Missing reachability detail is a proof deficiency (NEEDS_PROOF), not a fatal
flaw, so the conservative outcome is NEEDS_MORE_PROOF rather than a block.
"""
from __future__ import annotations

from _common import NEEDS_PROOF, PASS, GateResult, is_empty

GATE = 2
NAME = "attacker_reachability"


def evaluate(candidate: dict) -> list[GateResult]:
    missing: list[str] = []

    if is_empty(candidate.get("attacker_entrypoint")):
        missing.append("external attacker entrypoint")

    if is_empty(candidate.get("call_trace")):
        missing.append("exact call path (call_trace)")

    # preconditions can live in assumptions or attacker_capabilities
    if is_empty(candidate.get("assumptions")) and is_empty(candidate.get("attacker_capabilities")):
        missing.append("preconditions (assumptions / attacker_capabilities)")

    if is_empty(candidate.get("state_transition")):
        missing.append("state setup (state_transition)")

    # reason defenses do not block the path
    if is_empty(candidate.get("defense_analysis")):
        missing.append("reason defenses do not block the path (defense_analysis)")

    if missing:
        return [GateResult(
            GATE, NAME, NEEDS_PROOF,
            "Attacker reachability is under-specified; supply: " + "; ".join(missing),
            tag="reachability_incomplete",
            detail={"missing": missing},
        )]

    return [GateResult(
        GATE, NAME, PASS,
        "External entrypoint, call path, preconditions, state setup and defense "
        "bypass are all specified.",
    )]
