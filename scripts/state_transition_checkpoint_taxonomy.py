#!/usr/bin/env python3
"""
state_transition_checkpoint_taxonomy.py — P251 STATE_TRANSITION examine-time reasoning checkpoint (pure
classifier). Mirrors accounting_checkpoint_taxonomy.py (P249) EXACTLY in shape.

THIS IS A REASONING CHECKPOINT, NOT A DETECTOR. Given a function body it OBSERVES which of the five
state-transition families (S1-S5) the code shape belongs to and returns a structured
STATE_TRANSITION_CHECKPOINT *reasoning record*: the eight mandatory questions + empty hypothesis fields the
operator must fill. It NEVER returns a severity, a confidence, or a "vulnerable" verdict — firing only means
"adversarially trace this state transition before you move on." Adjudication happens later in the existing
precision pipeline on the operator-constructed candidate, never here. No I/O. No sixth family.
"""
from __future__ import annotations

QUESTIONS = [
    "Q1: Can an attacker choose the state transition?",
    "Q2: Can the transition be repeated?",
    "Q3: Does the transition overwrite another user's critical state?",
    "Q4: Does the transition grow an unbounded set or loop?",
    "Q5: Can two incompatible states both become true?",
    "Q6: Does a failure/shortfall branch still update state?",
    "Q7: Does a time-window change affect existing state?",
    "Q8: Who is harmed if this state persists?",
]

FAMILIES = ("S1_reset_overwrite_user_state", "S2_growable_set_unbounded_loop",
            "S3_dual_state_inconsistency", "S4_branch_consequence_not_traced",
            "S5_time_window_expiry_interaction")


def _has_any(text: str, markers) -> bool:
    return any(m in text for m in markers)


def _families(name: str, body: str, pat: dict) -> list[str]:
    """Two-signal shape detection per family (observe, not conclude)."""
    n = (name or "").lower()
    b = (body or "").lower()
    fams: list[str] = []
    f = pat["families"]

    s1 = f["S1_reset_overwrite_user_state"]
    if _has_any(b, s1["critical_var_markers"]) and _has_any(b, s1["overwrite_markers"]):
        fams.append("S1_reset_overwrite_user_state")

    s2 = f["S2_growable_set_unbounded_loop"]
    if _has_any(b, s2["set_markers"]) and _has_any(b, s2["iteration_markers"]):
        fams.append("S2_growable_set_unbounded_loop")

    s3 = f["S3_dual_state_inconsistency"]
    # require an opposing-state vocabulary in name+body AND a state write
    if _has_any(n + " " + b, s3["opposing_markers"]) and _has_any(b, s3["state_write_markers"]):
        fams.append("S3_dual_state_inconsistency")

    s4 = f["S4_branch_consequence_not_traced"]
    if _has_any(b, s4["branch_markers"]) and _has_any(b, s4["mutation_markers"]):
        fams.append("S4_branch_consequence_not_traced")

    s5 = f["S5_time_window_expiry_interaction"]
    if _has_any(n + " " + b, s5["time_var_markers"]) and _has_any(n + " " + b, s5["interaction_markers"]):
        fams.append("S5_time_window_expiry_interaction")

    return fams


def _shape_hints(family: str) -> tuple[str, str, str]:
    """Heuristic pre-fill of state_variable / triggering_action / invariant_expected from the shape ONLY.
    These are observations to seed reasoning — NOT conclusions."""
    if family == "S1_reset_overwrite_user_state":
        return ("a user-critical state var (e.g. unlockTime/status/balance)",
                "a write that overwrites the var (possibly on-behalf / by a non-owner)",
                "only the owner can worsen their own critical state; no third party can reset it")
    if family == "S2_growable_set_unbounded_loop":
        return ("a set/array/list that grows",
                "an action that appends to the set, later iterated in a loop",
                "the set size is bounded / the loop cannot be made unbounded by an attacker")
    if family == "S3_dual_state_inconsistency":
        return ("a pair of opposing flags/mappings (e.g. approve/disapprove, active/expired)",
                "a write to one side of the pair",
                "the two states are mutually exclusive (cannot both be true)")
    if family == "S4_branch_consequence_not_traced":
        return ("state written inside a failure/shortfall/else branch",
                "the branch executes on shortfall/failure and still mutates state/transfers",
                "a failure/shortfall branch must not leave protocol state inconsistent or move value wrongly")
    if family == "S5_time_window_expiry_interaction":
        return ("an expiry/duration/window variable",
                "an update or comparison of the time window interacting with existing state",
                "changing the window must not break, lock, or revert existing in-flight state")
    return ("", "", "")


def classify(contract: str, name: str, signature: str, body: str, *, patterns: dict) -> list[dict]:
    """
    Return a list of STATE_TRANSITION_CHECKPOINT reasoning records (possibly several families per function).

    Each record is INTERROGATIVE: it carries the eight questions and empty answer/hypothesis fields. It carries
    NO severity, NO confidence, NO verdict. `concluded` is always False and `requires_operator_reasoning` is
    always True — the checkpoint cannot conclude a vulnerability.
    """
    records: list[dict] = []
    for fam in _families(name, body, patterns):
        state_var, trig, inv = _shape_hints(fam)
        records.append({
            "output_type": "reasoning_record",
            "concluded": False,                 # invariant: a checkpoint never concludes
            "requires_operator_reasoning": True,
            "severity": None,                   # invariant: never set by the checkpoint
            "confidence": None,                 # invariant: never set by the checkpoint
            "state_family": fam,
            "contract": contract,
            "function": name,
            "state_variable": state_var,
            "pre_state": "",                    # operator fills
            "triggering_action": trig,
            "post_state": "",                   # operator fills
            "repeated_action_effect": "",       # operator fills
            "affected_actor": "",               # operator fills
            "invariant_expected": inv,
            "invariant_after_transition": "",   # operator fills
            "exploit_hypothesis": "",           # operator fills — this is the constructed candidate
            "questions": list(QUESTIONS),
        })
    return records
