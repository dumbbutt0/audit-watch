#!/usr/bin/env python3
"""
transferable_position_cap_bypass_taxonomy.py — pure (no-I/O) classifier for the TRANSFERABLE-POSITION CAP-BYPASS lens.

Generalized CLASS of the vultisig M-03 miss: a contract enforces a per-user cap (maxCapPerUser) where the per-user
accumulated amount is keyed on ownership of a TRANSFERABLE position NFT (ERC721). Transferring the NFT away resets
the cap (balanceOf -> 0), so a user re-buys and bypasses the per-user invariant.

Two-signal:  S1 a per-user cap term used in a check  AND  S2 position identity derived from transferable-NFT
ownership (balanceOf()/tokenOfOwnerByIndex()) in an ERC721 contract that does NOT block transfers (not soulbound).
Suppressions: view/pure; soulbound / non-transferable contracts; non-ERC721 contracts.

RESEARCH-ONLY (STAGED): read-only, is_gate:false, research_only:true, routes_in_production:false — never routes.
High precision over recall. Anchored on vultisig ILOPool.buy. is_erc721 / soulbound are supplied by the runner.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "transferable_position_cap_bypass_patterns.json"
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


def has_cap(text: str) -> bool:
    return bool(_any(strip_comments(text or "").lower(), _t("cap_terms", [])))


def is_view(signature: str) -> bool:
    s = strip_comments(signature or "").lower()
    return " view " in s or " pure " in s or "view returns" in s or "pure returns" in s


def classify(name: str, signature: str, file: str, contract: str, snippet: str = "",
             kind: str = "function", tags=None, is_erc721: bool = False, soulbound: bool = False) -> list:
    """Return 0..1 candidate. snippet = the (helper-resolved) body. Pure. is_erc721/soulbound from runner."""
    body = strip_comments(snippet or "").lower()
    sig = strip_comments(signature or "").lower()
    blob = body + " " + sig

    if kind == "library":
        return []
    if is_view(signature):
        return []
    # contract context: must be a transferable ERC721 position
    if not is_erc721 or soulbound:
        return []
    # ---- S1: a per-user cap term used in a check ----
    cap_hits = _any(blob, _t("cap_terms", []))
    if not cap_hits:
        return []
    if "require" not in body and "<=" not in body and "<" not in body and ">" not in body:
        return []
    # ---- S2: position identity from transferable-NFT ownership ----
    id_hits = _any(blob, _t("identity_markers", []))
    if not id_hits:
        return []

    return [{
        "finding_shape": "transferable_position_cap_bypass",
        "confidence": "high",
        "cap_term": cap_hits[0],
        "identity_marker": id_hits[0],
        "explanation": (f"{name} enforces a per-user cap ({cap_hits[0]}) keyed on transferable-NFT ownership "
                        f"({id_hits[0]}) in an ERC721 contract; transferring the position NFT resets the cap and "
                        f"lets a user re-buy, bypassing the per-user invariant — vultisig M-03 class."),
        "signals": {"S1_cap": cap_hits[:3], "S2_identity": id_hits[:3], "is_erc721": True, "soulbound": False},
        "suppression_status": "none",
    }]
