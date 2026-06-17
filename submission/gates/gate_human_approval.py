#!/usr/bin/env python3
"""
gate_human_approval.py — Gate 8: Human approval.

This gate encodes the layer's central invariant: the submission layer NEVER
autonomously submits. A human must approve before any submission, regardless
of how clean the candidate is.

It always returns PASS (it is not a blocker), but it:
  - records that no auto-submit path exists, and
  - notes if the candidate tried to assert human_approval_required=false.

The orchestrator additionally forces human_approval_required=true in its
output, so this can never be bypassed by an input file.
"""
from __future__ import annotations

from _common import PASS, WARN, GateResult

GATE = 8
NAME = "human_approval"


def evaluate(candidate: dict) -> list[GateResult]:
    if candidate.get("human_approval_required") is False:
        return [GateResult(
            GATE, NAME, WARN,
            "Candidate set human_approval_required=false; this is overridden — "
            "human approval is mandatory and the layer never auto-submits.",
            tag="approval_override",
        )]
    return [GateResult(
        GATE, NAME, PASS,
        "Human approval is mandatory before submission; the layer has no "
        "auto-submit path.",
    )]
