#!/usr/bin/env python3
"""
gate_defense.py — Gate 7: Invalidation / defense.

Requires:
  - a list of likely defenses (defense_analysis)
  - for each defense, why it fails or does not apply
  - any uncertainty clearly marked

Outcomes:
  - no defense_analysis at all                      -> NEEDS_PROOF
  - a defense that blocks the path with no rebuttal -> FAIL (DO_NOT_SUBMIT)
  - a defense without why_it_fails                  -> NEEDS_PROOF
  - uncertainty explicitly marked                   -> WARN (human review)
"""
from __future__ import annotations

from _common import FAIL, NEEDS_PROOF, PASS, WARN, GateResult, is_empty

GATE = 7
NAME = "invalidation_defense"


def evaluate(candidate: dict) -> list[GateResult]:
    results: list[GateResult] = []

    defenses = candidate.get("defense_analysis")
    if is_empty(defenses):
        return [GateResult(
            GATE, NAME, NEEDS_PROOF,
            "No defense analysis supplied; list likely defenses and why each fails "
            "or does not apply.",
            tag="defense_missing",
        )]

    blocking_unrebutted: list[str] = []
    unexplained: list[str] = []
    uncertain: list[str] = []

    for d in defenses:
        if not isinstance(d, dict):
            unexplained.append(str(d))
            continue
        name = d.get("defense", "<unnamed>")
        blocks = bool(d.get("blocks_path"))
        why = d.get("why_it_fails")
        if d.get("uncertain"):
            uncertain.append(name)
        if blocks and is_empty(why):
            blocking_unrebutted.append(name)
        elif is_empty(why) and not d.get("uncertain"):
            unexplained.append(name)

    if blocking_unrebutted:
        results.append(GateResult(
            GATE, NAME, FAIL,
            "A defense blocks the exploit path with no rebuttal: "
            + ", ".join(blocking_unrebutted),
            tag="defense_blocks_path",
            detail={"defenses": blocking_unrebutted},
        ))

    if unexplained:
        results.append(GateResult(
            GATE, NAME, NEEDS_PROOF,
            "Defenses listed without explaining why they fail/do not apply: "
            + ", ".join(unexplained),
            tag="defense_unexplained",
            detail={"defenses": unexplained},
        ))

    if uncertain:
        results.append(GateResult(
            GATE, NAME, WARN,
            "Defense applicability is explicitly uncertain (needs human review): "
            + ", ".join(uncertain),
            tag="defense_uncertain",
            detail={"defenses": uncertain},
        ))

    if not results:
        results.append(GateResult(
            GATE, NAME, PASS,
            "All likely defenses are listed and rebutted; no blocking defense remains.",
        ))
    return results
