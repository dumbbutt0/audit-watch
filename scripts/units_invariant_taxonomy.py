#!/usr/bin/env python3
"""
units_invariant_taxonomy.py — Single source of truth for classifying decimals/units/scaling invariant
surfaces. Used by units_invariant_audit.py. Mirrors cross_chain_taxonomy / token_standard_taxonomy.

This is a SEMANTIC MATH lens, not a flag-all-arithmetic sweep. The signal usually lives in the function
BODY (snippet), e.g. the #184 shape `reserve0.mul(1e18).div(reserve1)` — so the detector passes a source
snippet, and classify() looks at name + signature + snippet.

TWO-SIGNAL RULE (the false-positive backbone):
  units_sensitive := has_unit_context AND has_signal
where
  has_unit_context = a `unit_context_terms` word appears in name+snippet (amount/price/reserve/bdv/oracle/
                     shares/assets/rate/precision/decimal/twa/lp/...),
  has_signal       = a category's call/constant/arithmetic pattern matches,
UNLESS the category is `unambiguous` (decimals()/latestRoundData/convertToShares/pricePerShare/...), which
fires on the signal alone. This keeps bare 1e18, lone mulDiv, basis-points (100/10000) without amount
context, pure Math/PRBMath helpers, and loop-counter division OUT.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "units_invariant_patterns.json"

# names that are pure math/helper libraries — not protocol amount math on their own
_PURE_HELPER_HINTS = ("mulmod", "addmod", "sqrt", "log2", "exp2", "mostsignificantbit", "_mulmod")
_BASIS_POINTS = re.compile(r"\b(100|1000|10000|10_000|1e4|bps|basis)\b")


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"categories": {}, "unit_context_terms": [], "high_risk_categories": []}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def _has_unit_context(hay: str, terms: list[str]) -> bool:
    return any(t in hay for t in terms)


def _name_len(name_l: str, patterns: list[str]) -> int:
    best = 0
    for p in patterns:
        pl = p.lower()
        if pl and pl in name_l:
            best = max(best, len(pl))
    return best


def _matches(text: str, patterns: list[str]) -> bool:
    return any(p.lower() in text for p in patterns)


def _regex_any(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        try:
            if re.search(p, text, re.IGNORECASE):
                return True
        except re.error:
            continue
    return False


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    cats = tax.get("categories", {})
    terms = [t.lower() for t in tax.get("unit_context_terms", [])]
    name_l = (name or "").lower()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    body_l = body.lower()
    hay = " ".join([name_l, body_l, (file or "").lower(), (contract or "").lower(),
                    " ".join(tags or []).lower()])

    if any(h in name_l for h in _PURE_HELPER_HINTS):
        return _neg()
    has_ctx = _has_unit_context(hay, terms)

    hr = set(tax.get("high_risk_categories", []))
    best = None  # (sort_key, cat, meta, matched_on)
    for cat, meta in cats.items():
        nlen = _name_len(name_l, meta.get("name_patterns", []))
        name_hit = nlen > 0
        call_hit = _matches(body_l, [c.lower() for c in meta.get("call_patterns", [])])
        arith_hit = _regex_any(body, meta.get("arithmetic_patterns", []))
        unambiguous = bool(meta.get("unambiguous"))
        # TRIGGER = a real arithmetic/call signal in the BODY. A bare name or a lone constant is NOT a
        # trigger (a function named 'rate'/'getHumidity' or a stray 1e18 is not a units bug). Names &
        # constants only help pick the category. Unambiguous unit calls (decimals()/latestRoundData/
        # convertToShares/pricePerShare/virtualPrice) fire on the call alone; everything else needs the
        # scaling arithmetic shape AND a unit-context term (the two-signal rule).
        if unambiguous:
            if not call_hit:
                continue
        else:
            if not arith_hit:
                continue
            if not has_ctx:
                continue
        # specificity first: a specific category (reserve_units/twa_reserves/price_per_share/
        # division_before_multiplication/...) beats the generic 1e18 'assumed_18_decimals' fallback.
        spec = meta.get("specificity", 1)
        sig_rank = 3 if arith_hit else 2  # arith is the strongest signal
        key = (spec, sig_rank, nlen, 1 if cat in hr else 0)
        matched_on = "arith" if arith_hit else "call"
        if best is None or key > best[0]:
            best = (key, cat, meta, matched_on)

    if best is None:
        return _neg()
    _, cat, meta, matched_on = best
    return {
        "units_sensitive": True, "category": cat, "risk_tags": list(meta.get("risk_tags", [])),
        "review_hint": meta.get("review_hint", ""), "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
        "matched_on": matched_on,
    }


def _neg() -> dict:
    return {"units_sensitive": False, "category": None, "risk_tags": [], "review_hint": "",
            "severity_ceiling_hint": None, "matched_on": None}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    """High-risk = the category is in the curated high_risk set. (No risk_tag fallback — almost every
    units category carries a decimal_mismatch-ish tag, so a fallback would mark everything high-risk.)"""
    tax = taxonomy or load_taxonomy()
    if not classification.get("units_sensitive"):
        return False
    return classification.get("category") in tax.get("high_risk_categories", [])
