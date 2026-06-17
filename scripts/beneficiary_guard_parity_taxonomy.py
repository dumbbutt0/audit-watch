#!/usr/bin/env python3
"""
beneficiary_guard_parity_taxonomy.py — pure (no-I/O) helpers + classifier for the BENEFICIARY-GUARD PARITY lens.

Generalized CLASS of the P304 centrifuge M-04 miss: within one contract, some state-mutating functions guard a
beneficiary param with an owner-tied check (withApproval(owner) / require(msg.sender==owner)) while SIBLING functions
take a beneficiary param of the same role UNGUARDED -> a third party can act for the beneficiary (griefing/DoS).

Two-signal:  S1 the contract has >=1 owner-guarded beneficiary function (intent)  AND  S2 a sibling beneficiary
function is external + state-mutating + NOT owner-guarded + NOT admin-access-controlled.

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes. High precision over
recall. The per-contract correlation (S1 across siblings) is done by the audit runner; this module is pure.
Anchored on centrifuge LiquidityPool.deposit/mint vs requestDeposit/withdraw/redeem (withApproval).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "beneficiary_guard_parity_patterns.json"
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key: str, default):
    return _cfg().get(key, default)


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def beneficiary_param(signature: str) -> str | None:
    """Return the beneficiary role if the signature declares `address <role>` for a known role, else None."""
    sig = strip_comments(signature or "").lower()
    for role in _t("beneficiary_roles", []):
        if re.search(r"address\s+(_)?" + re.escape(role) + r"\b", sig):
            return role
    return None


def is_view(signature: str) -> bool:
    s = strip_comments(signature or "").lower()
    return any(m in s for m in _t("view_markers", []))


def is_external(signature: str, visibility: str) -> bool:
    v = (visibility or "").lower()
    if v in ("external", "public"):
        return True
    s = strip_comments(signature or "").lower()
    return " external" in s or " public" in s


def owner_guarded(signature: str, body: str) -> bool:
    s = strip_comments(signature or "").lower()
    b = strip_comments(body or "").lower()
    if any(m in s for m in _t("owner_guard_modifiers", [])):
        return True
    return any(c in b for c in _t("inline_self_check", []))


def admin_access_controlled(signature: str) -> bool:
    s = strip_comments(signature or "").lower()
    return any(m in s for m in _t("admin_access_modifiers", []))


def classify_function(name, signature, body, visibility, contract_has_owner_guard: bool) -> list:
    """S2 emission for one function, given S1 (the contract has an owner-guarded beneficiary sibling). Pure."""
    role = beneficiary_param(signature)
    if not role:
        return []
    if not contract_has_owner_guard:               # S1: no asymmetry without a guarded sibling
        return []
    if is_view(signature) or not is_external(signature, visibility):
        return []
    if owner_guarded(signature, body) or admin_access_controlled(signature):
        return []                                    # this function is itself guarded -> not the weak sibling
    return [{
        "finding_shape": "beneficiary_guard_parity",
        "confidence": "medium",
        "beneficiary_role": role,
        "explanation": (f"{name} takes a beneficiary param (address {role}) and is external + state-mutating but is "
                        f"NOT owner-guarded, while sibling functions in the same contract guard the beneficiary with "
                        f"an owner-tied check (withApproval/require(msg.sender==owner)). A third party can act for the "
                        f"beneficiary here (deposit/claim-for-others griefing — centrifuge M-04 class)."),
        "signals": {"S1_owner_guarded_sibling": True, "S2_unguarded_beneficiary": True},
        "suppression_status": "none",
    }]
