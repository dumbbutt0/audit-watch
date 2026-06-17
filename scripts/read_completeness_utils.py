#!/usr/bin/env python3
"""
read_completeness_utils.py — pure classifier for the P245 coverage read-completeness gate (#3).

The coverage disposition state machine ({unassigned,assigned,examined,cleared,finding,
deferred_out_of_scope}) records WHETHER an item was dispositioned, not whether its body was actually
read in full. This module adds an ORTHOGONAL `read_state` notion and a deterministic "critical item"
predicate so the gate can (optionally, default-off) block candidate triage until every CRITICAL in-scope
item is READ_FULL or explicitly justified.

Design mirrors gate_dos_utils.py / dependency_clear_utils.py: pure classification, no I/O, no disposition
writes, never mints a finding. The gate only consumes these helpers when the operator opts in via
--enforce-read-completeness or coverage_policy.enforce_read_completeness=true.

read_state is stored on the disposition record as an additive optional field (see
update_coverage_disposition.py). When absent, an item is treated as "not yet read in full".
"""
from __future__ import annotations

import re

# The 8 read-states from the P244 spec. READ_FULL/NOT_IN_SCOPE clear the coverage obligation outright;
# the *_ONLY / DUPLICATE_WRAPPER / BLOCKED_BY_* values are the "honesty" states: they let an item be
# cleared from the *coverage* obligation while remaining visibly UNREAD (with a recorded justification),
# so the true denominator stays visible.
ALLOWED_READ_STATES = {
    "READ_FULL",
    "READ_PARTIAL",
    "NOT_IN_SCOPE",
    "GENERATED_INTERFACE_ONLY",
    "DUPLICATE_WRAPPER",
    "BLOCKED_BY_SIZE",
    "BLOCKED_BY_BUILD",
    "BLOCKED_BY_MISSING_SOURCE",
}

# Name/identifier patterns for roles the manifest tag vocabulary does NOT cover directly
# (accounting/oracle/token/permissions/migration/config/decimals/cross_chain). Matched against the
# item name + signature (lowercased). Kept conservative — these are well-known security-critical shapes.
_HOOK_RE = re.compile(
    r"(on[a-z0-9]*received|_?(before|after)[a-z0-9]*(transfer|mint|burn|hook|action)"
    r"|fallback|receive|callback|hook|_check?on[a-z0-9]*received)",
    re.I,
)
_FALLBACK_RE = re.compile(r"\b(fallback|receive)\b", re.I)
_LIQUIDATION_RE = re.compile(r"liquidat|seize|repaywithcollateral", re.I)
_SETTLEMENT_RE = re.compile(r"settle|_settlepayment|fulfil|finaliz|reclaim|stoprent|payout|distribut", re.I)
_REWARD_RE = re.compile(r"reward|emission|gauge|notifyreward|checkpoint|accrue|claimrewards?|vest", re.I)
_UPGRADE_RE = re.compile(r"upgrade|initialize|reinitial|diamondcut|setimplementation|_authorizeupgrade", re.I)
_FACET_RE = re.compile(r"facet|selector|diamond", re.I)
_GUARDMOD_RE = re.compile(r"\b(guard|module|checktransaction|setguard|setfallbackhandler|enablemodule|disablemodule)\b", re.I)

# Mutability values that mean "does not change state" (so NOT a state-mutating entrypoint).
_NON_MUTATING = {"view", "pure", "constant"}


def _text(item: dict) -> str:
    return f"{item.get('name','')} {item.get('signature','')}".lower()


def is_critical(item: dict) -> bool:
    """True if the manifest item is on the P244 critical-item list (computed from existing fields)."""
    return bool(critical_reasons(item))


def critical_reasons(item: dict) -> list[str]:
    """Return the list of reasons the item is critical (empty list = not critical)."""
    reasons: list[str] = []
    vis = str(item.get("visibility", "")).lower()
    mut = str(item.get("mutability", "")).lower()
    tags = set(item.get("tags", []) or [])
    mods = [str(m).lower() for m in (item.get("modifiers") or [])]
    txt = _text(item)
    kind = str(item.get("kind", "")).lower()

    is_fn = kind in ("function", "initializer", "constructor")

    # public/external STATE-MUTATING entrypoints. (A bare public/external view/pure getter is NOT
    # treated as coverage-critical on its own — that would flag every getter and explode the critical
    # set / operator burden; risky getters are still caught by the specific category rules below, e.g.
    # an oracle/token/reward getter.)
    if is_fn and vis in ("public", "external") and mut not in _NON_MUTATING:
        reasons.append("state-mutating entrypoint")
    # privileged / admin
    if (mods and "permissions" in tags) or any(p in m for m in mods for p in
            ("onlyowner", "onlyrole", "auth", "admin", "onlygovernance", "restricted")):
        reasons.append("privileged/admin")
    # fallback / receive
    if _FALLBACK_RE.search(txt):
        reasons.append("fallback/receive")
    # hooks / callbacks
    if _HOOK_RE.search(txt):
        reasons.append("hook/callback")
    # token transfer / settlement paths
    if "token" in tags:
        reasons.append("token path")
    if _SETTLEMENT_RE.search(txt):
        reasons.append("settlement path")
    # oracle paths
    if "oracle" in tags:
        reasons.append("oracle path")
    # reward paths
    if _REWARD_RE.search(txt):
        reasons.append("reward path")
    # liquidation paths
    if _LIQUIDATION_RE.search(txt):
        reasons.append("liquidation path")
    # upgrade paths
    if _UPGRADE_RE.search(txt) or kind in ("constructor", "initializer"):
        reasons.append("upgrade/init path")
    # facets / selectors
    if _FACET_RE.search(txt) or "diamondcut" in txt:
        reasons.append("facet/selector")
    # module / guard paths
    if _GUARDMOD_RE.search(txt):
        reasons.append("module/guard path")
    return reasons


def read_state_satisfies_critical(disp: dict) -> tuple[bool, str]:
    """
    Does this disposition's read_state satisfy the critical-item coverage obligation?

    Returns (ok, reason). ok=False means the gate should block this critical item.
      READ_FULL / NOT_IN_SCOPE           -> ok
      GENERATED_INTERFACE_ONLY           -> ok IFF a justification is present
      DUPLICATE_WRAPPER                  -> ok IFF a canonical `duplicate_of` target is present
      BLOCKED_BY_*                       -> ok IFF read_block_reason AND read_block_ack (human ack) present
      READ_PARTIAL / missing / unknown   -> NOT ok
    """
    rs = (disp or {}).get("read_state")
    if rs in (None, ""):
        return False, "critical item has no read_state (not read in full)"
    if rs not in ALLOWED_READ_STATES:
        return False, f"critical item has invalid read_state '{rs}'"
    if rs in ("READ_FULL", "NOT_IN_SCOPE"):
        return True, ""
    if rs == "READ_PARTIAL":
        return False, "critical item only READ_PARTIAL"
    if rs == "GENERATED_INTERFACE_ONLY":
        if str(disp.get("generated_interface_reason") or "").strip():
            return True, ""
        return False, "GENERATED_INTERFACE_ONLY without justification"
    if rs == "DUPLICATE_WRAPPER":
        if str(disp.get("duplicate_of") or "").strip():
            return True, ""
        return False, "DUPLICATE_WRAPPER without canonical duplicate_of target"
    if rs.startswith("BLOCKED_BY_"):
        has_reason = str(disp.get("read_block_reason") or "").strip()
        has_ack = bool(disp.get("read_block_ack"))
        if has_reason and has_ack:
            return True, ""
        miss = []
        if not has_reason:
            miss.append("read_block_reason")
        if not has_ack:
            miss.append("read_block_ack (human acknowledgment)")
        return False, f"{rs} without {', '.join(miss)}"
    return False, f"unhandled read_state '{rs}'"
