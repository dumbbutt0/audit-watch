"""Phase-77 deep-pass state machine + forbidden-transition validator (RESEARCH-ONLY).

Ordered investigation states; a candidate may advance ONLY one step along the chain (or take a terminal off-ramp from the
appropriate stage). Every shortcut — most importantly STATIC_LEAD -> READY_FOR_HUMAN_REVIEW / POC_REQUIRED — raises
ForbiddenTransition. The forbidden shortcut `static lead -> finding` is structurally impossible.
"""
from __future__ import annotations

# linear progression states
PROGRESSION = [
    "STATIC_LEAD",
    "CONTEXT_MAPPED",
    "DEFENSE_TRACED",
    "EXPLOIT_PATH_ATTEMPTED",
    "IMPACT_CHECKED",
    "SOURCE_FALSIFIED",
]
# terminal outcomes
TERMINALS = {"REJECTED", "NEEDS_CONTEXT", "POC_REQUIRED", "READY_FOR_HUMAN_REVIEW"}

# which progression stages may legally drop to which terminal
_TERMINAL_FROM = {
    "REJECTED": {"DEFENSE_TRACED", "EXPLOIT_PATH_ATTEMPTED", "IMPACT_CHECKED", "SOURCE_FALSIFIED"},
    "NEEDS_CONTEXT": {"STATIC_LEAD", "CONTEXT_MAPPED", "DEFENSE_TRACED", "EXPLOIT_PATH_ATTEMPTED"},
    # promotion terminals ONLY from the final progression stage (after source falsification survived)
    "POC_REQUIRED": {"SOURCE_FALSIFIED"},
    "READY_FOR_HUMAN_REVIEW": {"SOURCE_FALSIFIED"},
}

FORBIDDEN_LABELS = ("confirmed bug", "valid finding", "submission ready", "submission-ready",
                    "CONFIRMED_BUG", "READY_TO_SUBMIT", "AUTO_SUBMIT")


class ForbiddenTransition(Exception):
    pass


def assert_transition(frm: str, to: str) -> None:
    """Permit only: next progression step, or a terminal off-ramp allowed from `frm`. Else raise ForbiddenTransition."""
    if frm not in PROGRESSION:
        raise ForbiddenTransition(f"unknown/terminal source state '{frm}'")
    if to in PROGRESSION:
        i = PROGRESSION.index(frm)
        if not (i + 1 < len(PROGRESSION) and PROGRESSION[i + 1] == to):
            raise ForbiddenTransition(f"illegal progression {frm} -> {to} (must be {PROGRESSION[i+1] if i+1<len(PROGRESSION) else 'TERMINAL'})")
        return
    if to in TERMINALS:
        if frm not in _TERMINAL_FROM[to]:
            raise ForbiddenTransition(f"illegal terminal transition {frm} -> {to} "
                                      f"(allowed from {sorted(_TERMINAL_FROM[to])})")
        return
    raise ForbiddenTransition(f"unknown target state '{to}'")


def assert_no_forbidden_label(text: str) -> None:
    low = (text or "").lower()
    for lab in FORBIDDEN_LABELS:
        if lab.lower() in low:
            raise ForbiddenTransition(f"forbidden promotion label present: '{lab}'")
