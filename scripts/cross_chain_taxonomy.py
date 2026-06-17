#!/usr/bin/env python3
"""
cross_chain_taxonomy.py — Single source of truth for classifying cross-chain / deployment-sensitive
constants (deterministic, no LLM). Used by BOTH build_coverage_manifest.py (inline manifest tagging)
and cross_chain_constants_audit.py (read-time detection), so the two never drift.

A constant/immutable/address-literal is classified by matching its declared NAME (case-insensitive
substring) and/or the assigned VALUE (regex) against config/cross_chain_constants.json. The point is to
surface values whose correctness depends on WHICH CHAIN the contract is deployed on — the class behind
eval misses #142 (BRIDGE), #133/#135 (token/oracle addr on L2), #320 (MERKLE_ROOT), #469 (block-time).

False-positive control (the primary design constraint): a NUMERIC constant is tagged ONLY when its name
implies cross-chain/oracle/season/timing semantics. Bare numeric literals (1e18, BDV_PRECISION, ONE_POINT,
loop counters) match no name pattern and carry no value pattern -> never tagged.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "cross_chain_constants.json"

ADDRESS_RE = re.compile(r"0x[a-fA-F0-9]{40}\b")
# names that mark a literal as a benign precision/scale constant even if it brushes a weak pattern
_BENIGN_NAME_HINTS = ("precision", "_scale", "scale_", "denominator", "one_point", "basis",
                      "max_uint", "min_uint", "wad", "ray", "bdv_", "stalk_", "gp_precision")


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"categories": {}, "numeric_timing_requires_context": True, "high_risk_categories": []}


def _extract_value(signature: str) -> str:
    """Best-effort: the RHS literal of `NAME = <value>;` (or the address literal in the line)."""
    if not signature:
        return ""
    m = re.search(r"=\s*([^;]+)", signature)
    rhs = m.group(1).strip() if m else signature
    am = ADDRESS_RE.search(rhs)
    if am:
        return am.group(0)
    # address(0)/address(0x0) placeholder -> canonical zero address (NOT numeric "0"), so a named
    # implementation/owner placeholder is recognised as an address literal rather than a number.
    if re.search(r"address\(\s*0x?0*\s*\)", rhs):
        return "0x" + "0" * 40
    if re.search(r"bytes32\(\s*0x?0*\s*\)", rhs):
        return "0x" + "0" * 64
    # bytes32 / numeric literal
    bm = re.search(r"(0x[a-fA-F0-9]+|\b\d[\d_]*(?:e\d+)?\b)", rhs)
    return bm.group(1).replace("_", "") if bm else ""


def _name_matches(name_l: str, patterns: list[str]) -> bool:
    for pat in patterns:
        # treat as substring unless it looks like an anchored/charclass regex
        if any(c in pat for c in "^$[]()|\\"):
            try:
                if re.search(pat, name_l):
                    return True
            except re.error:
                pass
        elif pat in name_l:
            return True
    return False


def _value_matches(value: str, patterns: list[str]) -> bool:
    for pat in patterns:
        try:
            if re.fullmatch(pat, value) or re.search(pat, value):
                return True
        except re.error:
            continue
    return False


def classify(name: str, signature: str = "", file: str = "", value: str | None = None,
             taxonomy: dict | None = None) -> dict:
    """Return {cross_chain_sensitive, category, risk_tags, severity_ceiling_hint, matched_on}.

    cross_chain_sensitive is False (category None) when nothing matches — the common case for the vast
    majority of harmless constants, keeping the manifest focused.
    """
    tax = taxonomy or load_taxonomy()
    cats = tax.get("categories", {})
    name_l = (name or "").lower()
    val = value if value is not None else _extract_value(signature)
    is_numeric_only = bool(val) and not val.lower().startswith("0x") and val.replace(".", "").isdigit()
    benign = any(h in name_l for h in _BENIGN_NAME_HINTS)

    hr_cats = set(tax.get("high_risk_categories", []))
    best = None  # (sort_key, category, meta, matched_on, name_hit)
    for cat, meta in cats.items():
        pats = [p.lower() for p in meta.get("name_patterns", [])]
        name_len = max((len(p) for p in pats if (re.search(p, name_l) if any(c in p for c in "^$[]()|\\")
                                                 else p in name_l)), default=0)
        name_hit = name_len > 0
        val_hit = bool(val) and _value_matches(val, meta.get("value_patterns", []))
        if not (name_hit or val_hit):
            continue
        # FP control: a numeric-only literal needs a NAME match (context), never value-only,
        # and never if the name marks it a benign precision/scale constant.
        if is_numeric_only and (benign or not name_hit):
            continue
        # A numeric value cannot be an address-based category (oracle_aggregator/l1_token/...). This
        # routes CHAINLINK_HEARTBEAT=3600 to 'heartbeat' (timing), not 'oracle_aggregator' (address).
        if is_numeric_only and "hardcoded_address" in meta.get("risk_tags", []):
            continue
        matched_on = "name+value" if (name_hit and val_hit) else ("name" if name_hit else "value")
        # Precedence: (1) name match beats value-only; (2) longest (most specific) name pattern;
        # (3) high-risk category; (4) stable. This makes L1_BLOCK_TIME -> block_time (len 13) beat
        # l1_token ("l1_", len 3), and a generic address fall to hardcoded_address (value-only).
        sort_key = (1 if name_hit else 0, name_len, 1 if cat in hr_cats else 0)
        if best is None or sort_key > best[0]:
            best = (sort_key, cat, meta, matched_on, name_hit)
    if best is None:
        return {"cross_chain_sensitive": False, "category": None, "risk_tags": [],
                "severity_ceiling_hint": None, "matched_on": None}
    _, cat, meta, matched_on, name_hit = best
    # Zero-address is benign for the GENERIC fallback (a bare address(0) is not chain-specific).
    # Name-matched categories (e.g. implementation placeholder WELL_IMPLMENTATION=address(0)) keep it.
    if cat == "hardcoded_address" and not name_hit and re.fullmatch(r"0x0{40}", val or ""):
        return {"cross_chain_sensitive": False, "category": None, "risk_tags": [],
                "severity_ceiling_hint": None, "matched_on": None}
    return {
        "cross_chain_sensitive": True,
        "category": cat,
        "risk_tags": list(meta.get("risk_tags", [])),
        "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
        "matched_on": matched_on,
    }


def risk_flags(classification: dict) -> dict:
    """Expand risk_tags into the explicit boolean fields the manifest carries."""
    rt = set(classification.get("risk_tags", []))
    return {
        "chain_specific": "chain_specific" in rt,
        "hardcoded_address": "hardcoded_address" in rt,
        "hardcoded_chain_assumption": "hardcoded_chain_assumption" in rt,
        "oracle_dependency": "oracle_dependency" in rt,
        "bridge_dependency": "bridge_dependency" in rt,
        "timing_dependency": "timing_dependency" in rt,
    }


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    tax = taxonomy or load_taxonomy()
    if not classification.get("cross_chain_sensitive"):
        return False
    if classification.get("category") in tax.get("high_risk_categories", []):
        return True
    rt = set(classification.get("risk_tags", []))
    return bool(rt & {"bridge_dependency", "oracle_dependency"})
