#!/usr/bin/env python3
"""
recipient_custody_taxonomy.py — classify asset-delivery compatibility risk in bridge/escrow code:
safe-vs-raw transfer, non-receiver lock (no onERC721Received/onERC1155Received capability check before a
safe delivery), and custody-released-but-trapped. Mirrors griefing_dos_taxonomy. The "no_retry_recovery"
category is contract-level and is decided by the audit runner (needs the whole-contract function set).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "recipient_custody_patterns.json"


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"delivery_signals": [], "safe_delivery_signals": [], "raw_delivery_signals": [],
                "receiver_check_signals": [], "custody_release_signals": [], "recovery_signals": [],
                "categories": {}}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", " ", text)


def _any(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        try:
            if re.search(p, text, re.IGNORECASE):
                return True
        except re.error:
            if p.lower() in text.lower():
                return True
    return False


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    name_l = (name or "").lower()

    has_safe = _any(body, tax.get("safe_delivery_signals", []))
    has_raw = _any(body, tax.get("raw_delivery_signals", []))
    has_delivery = has_safe or has_raw or _any(body, tax.get("delivery_signals", []))
    if not has_delivery:
        return {"recipient_custody_sensitive": False, "category": None, "role": None,
                "severity_ceiling_hint": None, "matched_on": None,
                "_has_safe": False, "_has_receiver_check": False, "_has_custody_release": False}

    has_receiver_check = _any(body, tax.get("receiver_check_signals", []))
    # `safeTransferFrom`/`onERC1155Received` themselves contain receiver-hook tokens; only count a check
    # that is NOT merely the delivery call itself (look for explicit Receiver-interface / isContract / code.length).
    explicit_check = _any(body, ["IERC721Receiver", "IERC1155Receiver", "isContract", "code\\.length", "supportsInterface"])
    has_custody_release = _any(body, tax.get("custody_release_signals", [])) or "escrow" in name_l

    if has_safe and not explicit_check:
        category = "non_receiver_lock"
    elif has_custody_release and has_delivery:
        category = "custody_released_but_trapped"
    elif has_raw and has_safe:
        category = "safe_vs_raw_transfer"
    elif has_raw:
        category = "safe_vs_raw_transfer"
    else:
        category = "non_receiver_lock" if has_safe else "safe_vs_raw_transfer"

    meta = tax.get("categories", {}).get(category, {})
    return {"recipient_custody_sensitive": True, "category": category, "role": "delivery",
            "severity_ceiling_hint": meta.get("severity_ceiling_hint", "Low"),
            "matched_on": "safe_delivery" if has_safe else "raw_delivery",
            "_has_safe": has_safe, "_has_receiver_check": explicit_check, "_has_custody_release": has_custody_release}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    """High-risk = a SAFE delivery to a recipient with NO explicit receiver-capability check (revert-lock),
    or a custody-release path delivering without a check."""
    if not classification.get("recipient_custody_sensitive"):
        return False
    if classification.get("category") == "non_receiver_lock" and classification.get("_has_safe") and not classification.get("_has_receiver_check"):
        return True
    if classification.get("category") == "custody_released_but_trapped" and not classification.get("_has_receiver_check"):
        return True
    return False
