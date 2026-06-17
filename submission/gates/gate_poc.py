#!/usr/bin/env python3
"""
gate_poc.py — Gate 4: Proof of Concept.

For High/Critical claims, requires:
  - a compiling or executable PoC (proof_type == runnable_poc, poc_status in
    {passing, compiling})
  - a PoC path
  - deterministic reproduction steps
  - before/after state or balance delta
  - clear attacker/victim setup

Hard-fails (FAIL -> DO_NOT_SUBMIT) on forbidden methods:
  - mainnet attack
  - public testnet abuse
  - fabricated / assumed-without-basis assumptions

Missing-but-not-forbidden proof -> NEEDS_PROOF.
"""
from __future__ import annotations

from _common import FAIL, NEEDS_PROOF, PASS, GateResult, contains_any, is_empty, text_blob

GATE = 4
NAME = "poc"

FORBIDDEN_METHOD_KEYWORDS = [
    "mainnet attack",
    "attack on mainnet",
    "exploit on mainnet",
    "live mainnet",
    "against mainnet",
    "public testnet",
    "testnet abuse",
    "live testnet",
    "real funds",
    "production deployment",
]

FABRICATION_KEYWORDS = [
    "fabricated",
    "made up",
    "made-up",
    "assumed value without",
    "guessed",
    "placeholder result",
    "faked",
    "hand-waved",
]

HIGH_SEVS = ("Critical", "High")


def evaluate(candidate: dict) -> list[GateResult]:
    results: list[GateResult] = []

    # forbidden testing methods are always fatal, regardless of severity
    blob = text_blob(
        candidate.get("invalidating_conditions"),
        candidate.get("reproduction_steps"),
        candidate.get("assumptions"),
        candidate.get("proof_type"),
    )
    forbidden = contains_any(blob, FORBIDDEN_METHOD_KEYWORDS)
    if forbidden:
        results.append(GateResult(
            GATE, NAME, FAIL,
            "PoC uses a forbidden method (no mainnet/public-testnet attacks): "
            + ", ".join(forbidden),
            tag="forbidden_poc_method",
            detail={"methods": forbidden},
        ))

    fabricated = contains_any(blob, FABRICATION_KEYWORDS)
    if fabricated:
        results.append(GateResult(
            GATE, NAME, FAIL,
            "PoC relies on fabricated assumptions: " + ", ".join(fabricated),
            tag="fabricated_poc",
            detail={"markers": fabricated},
        ))

    claim = candidate.get("severity_claim", "")
    proof_type = candidate.get("proof_type", "")
    poc_status = candidate.get("poc_status", "")

    if claim in HIGH_SEVS:
        missing: list[str] = []
        if proof_type != "runnable_poc":
            missing.append("a runnable PoC (proof_type=runnable_poc)")
        if poc_status not in ("passing", "compiling"):
            missing.append("a compiling/executable PoC (poc_status passing|compiling)")
        if is_empty(candidate.get("poc_path")):
            missing.append("a PoC path")
        if is_empty(candidate.get("reproduction_steps")):
            missing.append("deterministic reproduction steps")
        if is_empty(candidate.get("state_transition")) and is_empty(candidate.get("asset_delta")):
            missing.append("before/after state or balance delta")
        if is_empty(candidate.get("attacker_entrypoint")):
            missing.append("clear attacker setup (entrypoint)")
        if missing:
            results.append(GateResult(
                GATE, NAME, NEEDS_PROOF,
                f"'{claim}' finding lacks required PoC evidence: " + "; ".join(missing),
                tag="poc_required",
                detail={"missing": missing},
            ))

    if not results:
        results.append(GateResult(
            GATE, NAME, PASS,
            "PoC evidence is adequate for the claimed severity and uses no "
            "forbidden method.",
        ))
    return results
