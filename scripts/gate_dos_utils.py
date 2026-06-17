#!/usr/bin/env python3
"""
gate_dos_utils.py — adversarial "gate vs DoS" validator for clears.

A frequent miss-class (Panoptic M-01): a clear concludes that a revert/underflow/failed-check is an
*intended* gate ("solvent accounts underflow → can't be liquidated, that's the gate") without testing
whether the same revert blocks a LEGITIMATE actor — i.e. whether the "gate" is actually a liveness DoS.

This module detects clears that lean on an "intended revert/underflow", and requires a liveness disproof
before such a clear is allowed. Missing the disproof → route to needs_deep_pass with status note
`intended_gate_requires_liveness_disproof`. It NEVER mints a finding and NEVER touches non-gate clears.

Mirrors the shape of dependency_clear_utils.py: pure classification, no I/O, no disposition writes.
"""
from __future__ import annotations

import re

# Phrases that signal "this revert/underflow/failed-check is intentional / a gate".
INTENDED_GATE_PATTERNS = [
    r"intended\s+gate",
    r"acts?\s+as\s+(an?\s+)?(implicit\s+)?gate",
    r"implicit\s+gate",
    r"serves?\s+as\s+(an?\s+)?gate",
    r"reverts?\s+(as\s+)?(expected|intended|by\s+design)",
    r"designed\s+to\s+revert",
    r"(under|over)flow\s+(is\s+)?(intended|expected|by\s+design)",
    r"(under|over)flow\s+(here\s+)?(prevents|blocks|guards|gates)",
    r"revert\s+(here\s+)?(prevents|blocks|guards|gates)",
    r"(safe|fine|ok)\b[^.]*\brevert",
    r"blocks?\b[^.]*\bby\s+reverting",
    r"expected\s+(to\s+)?revert",
    r"reverts?\b[^.]*\b(intentional|on\s+purpose)",
    r"failed\s+check\s+(is\s+)?(intended|the\s+gate)",
]
INTENDED_GATE_RE = [re.compile(p, re.I) for p in INTENDED_GATE_PATTERNS]

# A liveness disproof must name which critical path the revert can (or cannot) block.
CRITICAL_PATHS = {
    "liquidation", "withdrawal", "withdraw", "settlement", "settle", "checkpointing", "checkpoint",
    "force_exercise", "forceexercise", "oracle_update", "oracle", "accounting_sync", "accounting",
    "bad_debt_handling", "bad_debt", "baddebt", "none",
}

# Fields the disproof must answer (flat on the disposition, or nested under `liveness_disproof`).
REQUIRED_LIVENESS_FIELDS = [
    "who_can_trigger",          # who can cause the revert (attacker / any user / privileged)
    "blocks_critical_path",     # which critical path it blocks, or "none"
    "one_user_blocks_others",   # can one user-controlled state block other users?
    "affects_liveness_path",    # does it sit on a liveness-critical path?
    "recovery_exists",          # is there a recovery / alternative path?
    "bounded_or_permanent",     # is the block bounded or permanent?
]

ROUTED_STATUS = "intended_gate_requires_liveness_disproof"


def _field(disp: dict, name: str):
    """Read a disproof field either flat on the disposition or nested under liveness_disproof."""
    proof = disp.get("liveness_disproof")
    if isinstance(proof, dict) and str(proof.get(name) or "").strip():
        return proof.get(name)
    return disp.get(name)


def is_intended_gate_clear(disp: dict) -> bool:
    """True if the clear's reasoning claims a revert/underflow/failed-check is intentional."""
    text = " ".join(str(disp.get(k) or "") for k in
                    ("clear_reason", "no_impact_reason", "guard_or_invariant", "reason"))
    return any(r.search(text) for r in INTENDED_GATE_RE)


def classify(disp: dict) -> dict:
    """
    Return {status, missing}.
      status: not_intended_gate | ok | missing_liveness_disproof
      missing: list of unanswered/invalid liveness fields (empty unless missing_liveness_disproof)
    """
    if not is_intended_gate_clear(disp):
        return {"status": "not_intended_gate", "missing": []}
    missing = [f for f in REQUIRED_LIVENESS_FIELDS if not str(_field(disp, f) or "").strip()]
    # blocks_critical_path, when answered, must name a recognized critical path (or "none").
    bcp = str(_field(disp, "blocks_critical_path") or "").lower()
    if bcp and "blocks_critical_path" not in missing and not any(p in bcp for p in CRITICAL_PATHS):
        missing.append("blocks_critical_path(must name a critical path or 'none')")
    if missing:
        return {"status": "missing_liveness_disproof", "missing": missing}
    return {"status": "ok", "missing": []}


def reason(cls: dict) -> str:
    return (f"intended-gate clear missing liveness/DoS disproof: {', '.join(cls['missing'])} — "
            f"prove the revert/underflow does not block a legitimate actor on a critical path, "
            f"or file a finding")
