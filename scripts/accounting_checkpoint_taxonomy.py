#!/usr/bin/env python3
"""
accounting_checkpoint_taxonomy.py — P249 ACCOUNTING examine-time reasoning checkpoint (pure classifier).

THIS IS A REASONING CHECKPOINT, NOT A DETECTOR. Given a function body it OBSERVES which of the five
accounting families (A1-A5) the code shape belongs to and returns a structured ACCOUNTING_CHECKPOINT
*reasoning record*: the six mandatory questions + empty hypothesis fields the operator must fill. It NEVER
returns a severity, a confidence, or a "vulnerable" verdict — firing only means "this accounting shape
warrants a reasoning record before you move on." Adjudication happens later in the existing precision pipeline
on the operator-constructed candidate, never here.

Mirrors the pure-classifier shape of create_time_reentrancy_taxonomy.py (no I/O). No sixth family.
"""
from __future__ import annotations

# The six mandatory questions (constant; the heart of the checkpoint — they force candidate construction).
QUESTIONS = [
    "Q1: Can value be created?",
    "Q2: Can value be destroyed?",
    "Q3: Can value be counted twice?",
    "Q4: Can another actor be deprived?",
    "Q5: Can rounding favor the wrong side?",
    "Q6: Can a repeated action amplify the effect?",
]

FAMILIES = ("A1_rounding_direction", "A2_conservation", "A3_double_counting",
            "A4_shared_balance_depletion", "A5_index_arithmetic_exactness")


def _has_any(text: str, markers) -> bool:
    return any(m in text for m in markers)


def _families(name: str, body: str, pat: dict) -> list[str]:
    """Two-signal shape detection per family (observe, not conclude)."""
    n = (name or "").lower()
    b = (body or "").lower()
    nb = n + " " + b
    fams: list[str] = []
    f = pat["families"]

    # A1 rounding-direction: a conversion/round op in a deposit/withdraw/mint/redeem/preview context
    a1 = f["A1_rounding_direction"]
    if _has_any(nb, a1["context_markers"]) and _has_any(b, a1["op_markers"]):
        fams.append("A1_rounding_direction")

    # A2 conservation: value created/destroyed shape (mint/burn/fee/harvest)
    a2 = f["A2_conservation"]
    if _has_any(nb, a2["context_markers"]) and _has_any(b, a2["op_markers"]):
        fams.append("A2_conservation")

    # A3 double-counting: a quantity read and re-added/carried
    a3 = f["A3_double_counting"]
    if _has_any(b, a3["quantity_markers"]) and _has_any(b, a3["reuse_markers"]):
        fams.append("A3_double_counting")

    # A4 shared-balance depletion: a shared/escrow/pool balance moved on behalf of one actor
    a4 = f["A4_shared_balance_depletion"]
    if _has_any(b, a4["shared_markers"]) and _has_any(b, a4["actor_op_markers"]):
        fams.append("A4_shared_balance_depletion")

    # A5 index/arithmetic exactness: length/index/slice arithmetic (off-by-one prone)
    a5 = f["A5_index_arithmetic_exactness"]
    if _has_any(b, a5["index_markers"]) and _has_any(b, a5["arith_markers"]):
        fams.append("A5_index_arithmetic_exactness")

    return fams


def _shape_hints(family: str, name: str, body: str) -> tuple[str, str, str, str]:
    """Heuristic pre-fill of value_source / value_sink / conservation_expected / affected_actor from the
    shape ONLY. These are observations to seed reasoning — NOT conclusions."""
    b = (body or "").lower()
    if family == "A1_rounding_direction":
        return ("input amount", "converted amount (shares/assets)",
                "rounding favors the protocol/vault (EIP-4626 directionality)", "depositor/withdrawer")
    if family == "A2_conservation":
        return ("minted/credited value", "burned/debited value",
                "total value in == total value out (no creation/destruction)", "all holders")
    if family == "A3_double_counting":
        return ("a stored quantity (remainder/reward/balance)", "the same quantity re-added in a later step",
                "each unit of value is counted exactly once", "the counting party vs other users")
    if family == "A4_shared_balance_depletion":
        return ("a shared/escrow/pool balance", "one actor's claim/withdrawal",
                "one actor cannot draw down balances owed to others", "other claimants")
    if family == "A5_index_arithmetic_exactness":
        return ("an index/length expression", "a slice/loop bound or check",
                "index/length arithmetic is exact (inclusive vs exclusive)", "callers of the affected check")
    return ("", "", "", "")


def classify(contract: str, name: str, signature: str, body: str, *, patterns: dict) -> list[dict]:
    """
    Return a list of ACCOUNTING_CHECKPOINT reasoning records (possibly several families per function).

    Each record is INTERROGATIVE: it carries the six questions and empty answer/hypothesis fields. It carries
    NO severity, NO confidence, NO verdict. `concluded` is always False and `requires_operator_reasoning` is
    always True — the checkpoint cannot conclude a vulnerability.
    """
    records: list[dict] = []
    for fam in _families(name, body, patterns):
        vsrc, vsink, cons_exp, actor = _shape_hints(fam, name, body)
        records.append({
            "output_type": "reasoning_record",
            "concluded": False,                 # invariant: a checkpoint never concludes
            "requires_operator_reasoning": True,
            "severity": None,                   # invariant: never set by the checkpoint
            "confidence": None,                 # invariant: never set by the checkpoint
            "accounting_family": fam,
            "contract": contract,
            "function": name,
            "value_source": vsrc,
            "value_sink": vsink,
            "conservation_expected": cons_exp,
            "conservation_actual": "",          # operator fills after answering the questions
            "affected_actor": actor,
            "potential_winner": "",             # operator fills
            "potential_loser": "",              # operator fills
            "exploit_hypothesis": "",           # operator fills — this is the constructed candidate
            "questions": list(QUESTIONS),
        })
    return records
