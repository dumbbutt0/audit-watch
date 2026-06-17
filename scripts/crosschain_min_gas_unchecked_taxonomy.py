#!/usr/bin/env python3
"""
crosschain_min_gas_unchecked_taxonomy.py — pure (no-I/O) classifier for the CROSS-CHAIN MIN-GAS lens.

Generalized CLASS of the P306 decent H-02 miss: a cross-chain send (LayerZero sendAndCall / lzSend / Stargate
router.swap) forwards a caller-supplied destination-gas amount (dstGasForCall) with NO minimum-gas floor, so an
underfunded value makes the destination execution fail (funds delivered, the call reverts).

Two-signal:  S1 a cross-chain send primitive  AND  S2 a destination-gas param/var forwarded without a floor
(no require(gas>=MIN) / min-gas constant).  Suppressions: pure view fee-estimators; an explicit min check; LZ libs.

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes. High precision over
recall. The +1-level helper resolution is done by the audit runner; this module is pure. Anchored on decent
DecentEthRouter.bridgeWithPayload/_bridgeWithPayload.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "crosschain_min_gas_unchecked_patterns.json"
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


def has_send(text: str) -> bool:
    return bool(_any(strip_comments(text or "").lower(), _t("send_primitives", [])))


def _has_min_check(blob: str, gas_terms) -> bool:
    if _any(blob, _t("min_gas_markers", [])):
        return True
    # a comparison flooring any gas term: `<gasterm> >= ...` or `... >= <gasterm>` or `<gasterm> > ...`
    for g in gas_terms:
        if re.search(re.escape(g) + r"\s*[<>]=?", blob) or re.search(r"[<>]=?\s*" + re.escape(g), blob):
            return True
    return False


def is_view(signature: str) -> bool:
    s = strip_comments(signature or "").lower()
    return " view " in s or " pure " in s or "view returns" in s or "pure returns" in s


def classify(name: str, signature: str, file: str, contract: str, snippet: str = "",
             kind: str = "function", tags=None) -> list:
    """Return 0..1 candidate. snippet = the (helper-resolved) body. Pure."""
    body = strip_comments(snippet or "").lower()
    sig = strip_comments(signature or "").lower()
    clow = (contract or "").lower()
    blob = body + " " + sig

    if kind == "library" or any(clow == n or clow.endswith(n) for n in _t("suppress_library_contracts", [])):
        return []
    # ---- S1: cross-chain send primitive ----
    send_hits = _any(blob, _t("send_primitives", []))
    if not send_hits:
        return []
    if is_view(signature):       # fee estimators are views
        return []
    # ---- S2: a destination-gas param/var forwarded, with no floor ----
    gas_terms = _t("gas_terms", [])
    gas_hits = _any(blob, gas_terms)
    if not gas_hits:
        return []
    if _has_min_check(blob, gas_terms):
        return []

    # confidence high when the gas value is a function parameter (caller-supplied)
    caller_supplied = any(g in sig for g in gas_terms) or "uint64" in sig or "uint256 _dstgas" in sig
    confidence = "high" if caller_supplied else "medium"
    return [{
        "finding_shape": "crosschain_min_gas_unchecked",
        "confidence": confidence,
        "send_primitive": send_hits[0],
        "gas_param": gas_hits[0],
        "explanation": (f"{name} performs a cross-chain send ({send_hits[0]}) forwarding a destination-gas amount "
                        f"({gas_hits[0]}) with no minimum-gas floor; an underfunded dst-gas value makes the "
                        f"destination execution revert (funds delivered, call fails) — decent H-02 class."),
        "signals": {"S1_send": send_hits[:3], "S2_gas_param": gas_hits[:3], "min_check": False},
        "suppression_status": "none",
    }]
