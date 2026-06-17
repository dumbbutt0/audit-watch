#!/usr/bin/env python3
"""
token_standard_taxonomy.py — Single source of truth for classifying token-standard interaction surfaces
(ERC1155 / ERC721 / ERC20 / custom wrappers). Used by token_standard_audit.py (and any future builder
integration). Mirrors cross_chain_taxonomy.py.

The point is token-standard SEMANTIC risk (receiver-revert DoS, mint-to-non-receiver stuck tokens, batch
length mismatch, supply-vs-ownership accounting, operator bypass, cross-standard id confusion) — the class
behind eval misses #272 (Fertilizer ERC1155 NFT loss) and #273 (ERC1155 mint DoS) that a generic
"standard OZ code" clear misses.

Disambiguation + FP controls (the design constraints):
  * Standard is inferred from the function-signature PARAM SHAPE (ids/amounts -> 1155 batch; id+amount[+data]
    -> 1155 single; tokenId-only -> 721; amount-only/no-id -> 20) plus interface/inherit/file CONTEXT. This
    keeps ERC20 transferFrom(from,to,amount) out of the ERC1155 bucket and vice-versa.
  * Bare "transfer" is NOT a pattern (would hit Beanstalk transferStalk/transferDeposit/transferPlot). Only
    specific names (transferfrom/safetransferfrom/safebatchtransferfrom/_mint/_mintbatch/...) match.
  * URI/metadata names -> erc1155_uri_metadata (Low, metadata_only) — not mint/transfer risk.
  * receiver-callback IMPLEMENTATION (onERC1155Received) is a separate category from the acceptance-check
    CALLER (_doSafeTransferAcceptanceCheck).
  * A bare local `id` / `token` name with no standard call/interface context is NOT tagged.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "token_standard_patterns.json"

# names that are domain logic, not token-standard calls, even if they brush a weak pattern
_BENIGN_NAME_HINTS = ("transferstalk", "transferdeposit", "transferplot", "transferinternal",
                      "transferownership", "transfertoken_", "transferroots")


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"categories": {}, "high_risk_categories": [], "standard_hints": {}}


def _param_shape(signature: str) -> dict:
    """Infer token-call shape from the declaration/param list (best-effort)."""
    s = (signature or "").lower()
    inner = ""
    m = re.search(r"\(([^)]*)\)", s)
    if m:
        inner = m.group(1)
    return {
        "has_ids": bool(re.search(r"\bids\b|uint\d*\[\]\s*\w*ids|memory ids|\[\]\s*ids", inner)) or "ids" in inner.split(","),
        "has_amounts": "amounts" in inner,
        "has_id": bool(re.search(r"\bid\b|\btokenid\b", inner)),
        "has_amount": bool(re.search(r"\bamount\b|\bvalue\b", inner)),
        "has_data": bool(re.search(r"\bdata\b", inner)),
        "has_tokenid": "tokenid" in inner,
        "n_commas": inner.count(",") if inner.strip() else -1,
    }


def _context_standard(haystack: str, tax: dict) -> str:
    hints = tax.get("standard_hints", {})
    # check ERC1155 first (most specific), then 721, then 20
    for std in ("ERC1155", "ERC721", "ERC20"):
        for h in hints.get(std, []):
            if h in haystack:
                return std
    return "UNKNOWN"


def _shape_standard(shape: dict) -> str:
    if shape["has_amounts"] or (shape["has_ids"] and shape["has_amounts"]):
        return "ERC1155"  # batch (amounts plural is 1155-specific)
    if shape["has_ids"]:
        return "ERC1155"
    if shape["has_id"] and shape["has_amount"]:
        return "ERC1155"
    if shape["has_data"] and (shape["has_id"] or shape["has_tokenid"]) and shape["has_amount"]:
        return "ERC1155"
    if (shape["has_tokenid"] or shape["has_id"]) and not shape["has_amount"]:
        return "ERC721"
    if shape["has_amount"] and not (shape["has_id"] or shape["has_tokenid"] or shape["has_ids"]):
        return "ERC20"
    return "UNKNOWN"


def _name_match_len(name_l: str, patterns: list[str]) -> int:
    best = 0
    for pat in patterns:
        p = pat.lower()
        if any(c in p for c in "^$[]()|\\"):
            try:
                if re.search(p, name_l):
                    best = max(best, len(p))
            except re.error:
                pass
        elif p in name_l:
            best = max(best, len(p))
    return best


def _any_in(haystack: str, patterns: list[str]) -> bool:
    return any(p.lower() in haystack for p in patterns)


def _event_hit(signature: str, events: str, patterns: list[str]) -> bool:
    """Case-sensitive word-boundary event match so 'LibTransfer.To' does NOT match 'Transfer'."""
    text = (signature or "") + " " + (events or "")
    for ev in patterns:
        if re.search(r"\b" + re.escape(ev) + r"\b", text):
            return True
    return False


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             calls: str = "", events: str = "", taxonomy: dict | None = None) -> dict:
    """Return {token_standard_sensitive, standard, category, risk_tags, review_hint,
    severity_ceiling_hint, matched_on}."""
    tax = taxonomy or load_taxonomy()
    cats = tax.get("categories", {})
    name_l = (name or "").lower()
    sig_l = (signature or "").lower()
    extra = " ".join([calls or "", events or ""]).lower()
    hay = " ".join([name_l, sig_l, (file or "").lower(), (contract or "").lower(), extra])

    if any(b in name_l for b in _BENIGN_NAME_HINTS):
        return _neg()

    shape = _param_shape(signature)
    ctx_std = _context_standard(hay, tax)
    shp_std = _shape_standard(shape)
    # Context (interface/inherit/file e.g. Fertilizer1155.sol, IERC1155) is a stronger signal than
    # param-shape for accessors like totalSupply(id)/uri(id); shape is the fallback when no context.
    final_std = ctx_std if ctx_std != "UNKNOWN" else shp_std

    hr = set(tax.get("high_risk_categories", []))
    best = None  # (sort_key, cat, meta, matched_on)
    for cat, meta in cats.items():
        nlen = _name_match_len(name_l, meta.get("name_patterns", []))
        name_hit = nlen > 0
        call_hit = _any_in(sig_l + " " + extra, meta.get("call_patterns", []))
        event_hit = _event_hit(signature, events, meta.get("event_patterns", []))
        if not (name_hit or call_hit or event_hit):
            continue
        cat_std = meta.get("standard", "UNKNOWN")
        # require_standard_context: shared/generic-named categories (e.g. erc1155_mint via "_mint",
        # erc1155_transfer via "safetransferfrom") only fire when the standard is POSITIVELY inferred
        # (shape or interface/file context) and matches this category. This is the core FP control:
        # a Silo deposit/balanceOf with no ERC1155 shape/context is NOT tagged. A unique call/event
        # signal (e.g. _doSafe*AcceptanceCheck) overrides the context requirement.
        if meta.get("require_standard_context") and not (call_hit or event_hit):
            if cat_std != final_std:
                continue
        # standard disambiguation: positively-inferred standard conflicts with this category's
        # standard -> skip, unless matched on a unique call/event signal.
        if final_std != "UNKNOWN" and cat_std not in (final_std, "CUSTOM"):
            if not (call_hit or event_hit):
                continue
        # sort: name>call>event ; longest name ; standard matches inferred ; high-risk ; stable
        sig_rank = 3 if name_hit else (2 if call_hit else 1)
        std_match = 1 if cat_std == final_std else 0
        key = (sig_rank, nlen, std_match, 1 if cat in hr else 0)
        matched_on = "name" if name_hit else ("call" if call_hit else "event")
        if best is None or key > best[0]:
            best = (key, cat, meta, matched_on)

    if best is None:
        return _neg()
    _, cat, meta, matched_on = best
    std = meta.get("standard", "UNKNOWN")
    if std == "CUSTOM":
        std = "CUSTOM"
    elif final_std != "UNKNOWN":
        std = final_std
    return {
        "token_standard_sensitive": True,
        "standard": std,
        "category": cat,
        "risk_tags": list(meta.get("risk_tags", [])),
        "review_hint": meta.get("review_hint", ""),
        "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
        "matched_on": matched_on,
    }


def _neg() -> dict:
    return {"token_standard_sensitive": False, "standard": "UNKNOWN", "category": None,
            "risk_tags": [], "review_hint": "", "severity_ceiling_hint": None, "matched_on": None}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    tax = taxonomy or load_taxonomy()
    if not classification.get("token_standard_sensitive"):
        return False
    if classification.get("category") in tax.get("high_risk_categories", []):
        return True
    rt = set(classification.get("risk_tags", []))
    return bool(rt & {"receiver_dos", "stuck_tokens", "cross_standard", "acceptance_check"})
