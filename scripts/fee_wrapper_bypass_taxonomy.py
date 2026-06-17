#!/usr/bin/env python3
"""
fee_wrapper_bypass_taxonomy.py — pure (no-I/O) classifier for the FEE-WRAPPER BYPASS lens (CONSERVATIVE / low-precision).

Generalized CLASS of the P306 decent M-02 miss: a fee/validation layer wraps an underlying cross-chain action, but
that action is itself PUBLIC with no caller restriction, so users bypass the fee by calling the underlying directly.

Two-signal:  S1 (scope) a fee layer exists  AND  S2 (per-fn) a public cross-chain action with no access modifier
that does not itself invoke the fee layer.  Fire LOW confidence. Suppressions: access modifier; fee-invoking fn;
no fee layer; views.

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes. Lowest-precision lens;
advisory only. The scope-level fee-layer detection + helper resolve are done by the runner; this module is pure.
Anchored on decent DecentEthRouter.bridge/bridgeWithPayload (public) + UTBFeeCollector.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "fee_wrapper_bypass_patterns.json"
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


def _any(text: str, terms) -> list:
    return [w for w in terms if w in text]


def is_fee_layer_contract(contract: str, blob: str) -> bool:
    clow = (contract or "").lower()
    if any(t in clow for t in _t("fee_layer_contract_terms", [])):
        return True
    return bool(_any((blob or "").lower(), _t("fee_layer_fn_terms", [])))


def _name_is_action(name: str) -> bool:
    nl = (name or "").lower()
    for v in _t("action_verbs", []):
        if nl == v:
            return True
        if nl.startswith(v) and len(name) > len(v):
            nxt = name[len(v)]
            if nxt.isupper() or not nxt.isalpha():
                return True
    return False


def is_view(signature: str) -> bool:
    s = strip_comments(signature or "").lower()
    return " view " in s or " pure " in s or "view returns" in s or "pure returns" in s


def is_external(signature: str, visibility: str) -> bool:
    v = (visibility or "").lower()
    if v in ("external", "public"):
        return True
    s = strip_comments(signature or "").lower()
    return " external" in s or " public" in s


def classify(name, signature, file, contract, snippet="", kind="function", tags=None,
             has_fee_layer: bool = False, visibility: str = "") -> list:
    """S2 emission for one function, given S1 (scope has a fee layer). Pure."""
    if not has_fee_layer:
        return []
    sig = strip_comments(signature or "").lower()
    body = strip_comments(snippet or "").lower()
    if is_view(signature) or not is_external(signature, visibility):
        return []
    if not _name_is_action(name):
        return []
    if any(m in sig for m in _t("access_modifiers", [])):
        return []                                   # access-controlled -> not an open bypass
    if _any(sig + " " + body, _t("fee_invocation_terms", [])):
        return []                                   # this IS the fee-charging entrypoint
    if not _any(body, _t("send_primitives", [])):
        return []                                   # confirm it really performs the cross-chain action
    return [{
        "finding_shape": "fee_wrapper_bypass",
        "confidence": "low",
        "explanation": (f"{contract}.{name} is a PUBLIC cross-chain action with no caller restriction, while the "
                        f"codebase has a fee/validation layer (FeeCollector/collectFees) that wraps this action — "
                        f"users can bypass the fee by calling {name} directly (decent M-02 class). Advisory/low "
                        f"precision: confirm the action is meant to be fee-gated."),
        "signals": {"public_action": name, "fee_layer_in_scope": True, "no_access_modifier": True},
        "suppression_status": "none",
    }]
