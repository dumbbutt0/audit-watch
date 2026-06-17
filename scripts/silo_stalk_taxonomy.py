#!/usr/bin/env python3
"""
silo_stalk_taxonomy.py — Single source of truth for classifying Silo stalk/stem conservation surfaces.
Used by silo_stalk_audit.py. Mirrors getter_state_taxonomy / units_invariant_taxonomy.

This models CONSERVATION of deposit amount, BDV, stem, stalk, grown-stalk, roots, seeds and reward scaling
across Silo transfer/reward/germination flows — not a "find stalk words" scan. The signal lives in the
function BODY (snippet), so the detector passes a source snippet and classify() looks at name + signature +
snippet + contract + file.

TWO-GATE FP backbone:
  silo_stalk_sensitive := has_silo_domain AND has_accounting_signal
where
  has_silo_domain    = a silo_domain_terms word in name/snippet/contract, OR the file sits under a
                       silo_path_hints directory;
  has_accounting_signal = a category's call_patterns or arithmetic_patterns match the BODY (a real
                       call / arithmetic / state-transition — NOT a bare storage read). name_patterns and
                       state_var_patterns only refine the category, they never trigger on their own.
Generic ERC20 ops (transfer/approve/balanceOf) with no stalk/stem/deposit/bdv/roots context are dropped;
comments are stripped; a bare `return s.x` getter has no accounting signal -> excluded (only getters that
COMPUTE stalk/stem/reward are tagged).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "silo_stalk_patterns.json"

_GENERIC_ERC20 = ("transfer", "transferfrom", "approve", "allowance", "balanceof",
                  "increaseallowance", "decreaseallowance", "totalsupply", "permit")
_ACCT_TERMS = ("stalk", "stem", "deposit", "bdv", "roots", "seeds", "germinat", "grown")


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"categories": {}, "silo_domain_terms": [], "silo_path_hints": [],
                "high_risk_categories": [], "cross_function_invariants": []}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def _matches(text: str, patterns: list[str]) -> bool:
    return any(p.lower() in text for p in patterns)


def _is_regexy(p: str) -> bool:
    return bool(re.search(r"[\\\[\](){}^$|?*+]", p))


def _regex_any(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        try:
            if re.search(p, text, re.IGNORECASE):
                return True
        except re.error:
            continue
    return False


def _name_len(name_l: str, patterns: list[str]) -> int:
    best = 0
    for p in patterns:
        pl = p.lower()
        if pl and pl in name_l:
            best = max(best, len(pl))
    return best


def _signal_hit(body_l: str, body: str, meta: dict) -> bool:
    calls = meta.get("call_patterns", [])
    arith = meta.get("arithmetic_patterns", [])
    sub_calls = [c for c in calls if not _is_regexy(c)]
    rx_calls = [c for c in calls if _is_regexy(c)]
    return (_matches(body_l, [c.lower() for c in sub_calls])
            or _regex_any(body, rx_calls) or _regex_any(body, arith))


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", mutability: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    cats = tax.get("categories", {})
    terms = [t.lower() for t in tax.get("silo_domain_terms", [])]
    hints = [h.lower() for h in tax.get("silo_path_hints", [])]
    name_l = (name or "").lower()
    file_l = (file or "").lower()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    body_l = body.lower()
    ctx = " ".join([name_l, body_l, (contract or "").lower(), " ".join(tags or []).lower()])

    has_domain = any(t in ctx for t in terms) or any(h in file_l for h in hints)
    if not has_domain:
        return _neg()

    # FP: generic ERC20 op with no Silo-accounting context in the body
    if name_l in _GENERIC_ERC20 and not any(t in body_l for t in _ACCT_TERMS):
        return _neg()

    hr = set(tax.get("high_risk_categories", []))
    best = None
    for cat, meta in cats.items():
        if not _signal_hit(body_l, body, meta):
            continue
        nlen = _name_len(name_l, meta.get("name_patterns", []))
        path_hit = any(p.lower() in file_l for p in meta.get("path_patterns", []))
        state_hit = _matches(body_l, [s.lower() for s in meta.get("state_var_patterns", []) if not _is_regexy(s)])
        spec = meta.get("specificity", 1)
        key = (spec, nlen, 1 if path_hit else 0, 1 if state_hit else 0, 1 if cat in hr else 0)
        if best is None or key > best[0]:
            best = (key, cat, meta)

    if best is None:
        return _neg()
    _, cat, meta = best
    return {
        "silo_stalk_sensitive": True,
        "category": cat,
        "accounting_domains": list(meta.get("accounting_domains", [])),
        "risk_tags": list(meta.get("risk_tags", [])),
        "review_hint": meta.get("review_hint", ""),
        "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
        "matched_on": "signal",
    }


def _neg() -> dict:
    return {"silo_stalk_sensitive": False, "category": None, "accounting_domains": [], "risk_tags": [],
            "review_hint": "", "severity_ceiling_hint": None, "matched_on": None}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    tax = taxonomy or load_taxonomy()
    if not classification.get("silo_stalk_sensitive"):
        return False
    return classification.get("category") in tax.get("high_risk_categories", [])
