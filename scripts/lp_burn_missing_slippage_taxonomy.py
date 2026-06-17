#!/usr/bin/env python3
"""
lp_burn_missing_slippage_taxonomy.py — pure (no-I/O) classifier for the LP-BURN MISSING-SLIPPAGE lens.

Generalized CLASS of the vultisig M-02 miss: a position-management function withdraws user liquidity via a
Uniswap-V3-style pool.burn()/decreaseLiquidity() and forwards the resulting amount0/amount1 to a user with NO
amountMin/slippage bound -> the withdrawal can be MEV-sandwiched (user gets less than fair value).

Two-signal:  S1 a burn / decrease-liquidity primitive  AND  S2 NO slippage floor (no amount0Min/amount1Min param,
no 'slippage' marker, no min-amount comparison) in the function or a +1-level helper.
Suppressions: view/pure; functions that take/check a slippage bound (the mint/addLiquidity path); uniswap math libs.

RESEARCH-ONLY (STAGED): read-only, is_gate:false, research_only:true, routes_in_production:false — never routes.
High precision over recall. Anchored on vultisig ILOPool.claim.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "lp_burn_missing_slippage_patterns.json"
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


def has_burn(text: str) -> bool:
    return bool(_any(strip_comments(text or "").lower(), _t("burn_primitives", [])))


def is_view(signature: str) -> bool:
    s = strip_comments(signature or "").lower()
    return " view " in s or " pure " in s or "view returns" in s or "pure returns" in s


def _has_slippage(blob: str, sig: str) -> bool:
    markers = _t("slippage_markers", [])
    if _any(blob, markers) or _any(sig, markers):
        return True
    return False


def classify(name: str, signature: str, file: str, contract: str, snippet: str = "",
             kind: str = "function", tags=None) -> list:
    """Return 0..1 candidate. snippet = the (helper-resolved) body. Pure."""
    body = strip_comments(snippet or "").lower()
    sig = strip_comments(signature or "").lower()
    clow = (contract or "").lower()
    blob = body + " " + sig

    if kind == "library" or any(clow == n or clow.endswith(n) for n in _t("suppress_library_contracts", [])):
        return []
    # ---- S1: a burn / decrease-liquidity primitive IN A UNISWAP-V3 LIQUIDITY CONTEXT ----
    # (an ERC20 token .burn(amount) is NOT this class; require LP context so debt/credit burns don't FP)
    burn_hits = _any(blob, _t("burn_primitives", []))
    if not burn_hits:
        return []
    if not _any(blob, _t("lp_context_markers", [])):
        return []
    if is_view(signature):
        return []
    # ---- S2: NO slippage floor in the function/helper ----
    if _has_slippage(blob, sig):
        return []

    # confidence high when the withdrawn amounts are paid out to a user in the same body
    pays_user = bool(_any(blob, _t("user_payout_markers", [])))
    confidence = "high" if pays_user else "medium"
    return [{
        "finding_shape": "lp_burn_missing_slippage",
        "confidence": confidence,
        "burn_primitive": burn_hits[0],
        "explanation": (f"{name} withdraws liquidity ({burn_hits[0]}) and forwards the returned amounts with no "
                        f"amountMin/slippage bound; the burn can be MEV-sandwiched so the user receives less than "
                        f"fair value — vultisig M-02 class."),
        "signals": {"S1_burn": burn_hits[:3], "S2_slippage_floor": False, "pays_user": pays_user},
        "suppression_status": "none",
    }]
