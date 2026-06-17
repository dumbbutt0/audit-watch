#!/usr/bin/env python3
"""
defi_accounting_taxonomy.py — Classifier for DeFi debt/credit CONSERVATION surfaces in accounting-heavy
protocols (Zaros-class perps + market-making). Used by defi_accounting_audit.py. Mirrors the prior lens
taxonomies (snippet-aware, like griefing/units/migration).

The question is NOT "does the function mention debt". It is "does this function MOVE/COMPUTE an accounting
quantity (debt, credit, capacity, assets, rewards, liquidity, pnl) such that it could become inconsistent
with the matching ledger side or with a global total across functions?" — the class behind the Zaros eval
miss cluster (settleVaultsDebt, withdrawUsdTokenFromMarket, getRealizedDebtUsd, recalculateVaultsCreditCapacity,
rebalanceVaultsAssets, AutoDeleverageFactor, WETH reward distribution, usdcAvailableForEngine lockup).

FP backbone (the spec's controls):
  * TWO-SIGNAL GATE: an item is accounting-sensitive only with (1) an accounting-DOMAIN signal (a debt/credit/
    capacity/asset/reward/liquidity state var or call) AND (2) a STATE-TRANSITION or non-trivial ARITHMETIC
    signal (a write/`+=`/`.add`/`.sub`/cast/oracle-scaled mul-div on accounting state). A bare name is never
    enough; a pure getter that only returns stored config is suppressed.
  * Simple getters (view/pure) that just return a stored value, plain `balanceOf` reads, generic ERC20
    transfers not tied to ledger state, admin config setters, and comments are NOT tagged.
  * HIGH-RISK additionally requires a high-risk category and (transition OR signed/unsigned OR oracle-scale).
Comments are stripped before matching.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "defi_accounting_patterns.json"

_ADMIN_HINTS = ("onlyowner", "_authorizeupgrade", "ownableupgradeable")
_SIMPLE_GETTER_RE = re.compile(r"\breturn\b", re.IGNORECASE)


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"categories": {}, "high_risk_categories": [], "accounting_domain_signals": [],
                "state_transition_signals": [], "arithmetic_signals": [], "signed_unsigned_signals": [],
                "oracle_scale_signals": [], "cross_function_invariants": []}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", " ", text)


def _name_len(name_l: str, patterns: list[str]) -> int:
    best = 0
    for p in patterns:
        pl = p.lower()
        if pl and pl in name_l:
            best = max(best, len(pl))
    return best


def _any(text: str, patterns: list[str]) -> bool:
    return any(p.lower() in text for p in patterns)


def _regex_any(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        try:
            if re.search(p, text, re.IGNORECASE):
                return True
        except re.error:
            if p.lower() in text.lower():
                return True
    return False


# domain → which of the 17 accounting domains it belongs to (for accounting_domains output)
def has_domain_signal(body_l: str, tax: dict) -> bool:
    return _any(body_l, tax.get("accounting_domain_signals", []))


def has_transition_signal(body: str, tax: dict) -> bool:
    return _regex_any(body, tax.get("state_transition_signals", []))


def has_signed_unsigned(body: str, tax: dict) -> bool:
    return _regex_any(body, tax.get("signed_unsigned_signals", []))


def has_oracle_scale(body_l: str, tax: dict) -> bool:
    return _any(body_l, tax.get("oracle_scale_signals", []))


def _is_simple_getter(signature: str, body: str, tax: dict) -> bool:
    """A view/pure that only returns a stored value and performs no accounting transition/arith."""
    sig_head = (signature or "").split("{", 1)[0].lower()
    read_only = bool(re.search(r"\b(view|pure)\b", sig_head))
    if not read_only:
        return False
    # if it computes (mul/div/add/sub/cast) it is NOT a simple getter
    if has_transition_signal(body, tax) or has_signed_unsigned(body, tax):
        return False
    if _regex_any(body, tax.get("arithmetic_signals", [])):
        return False
    return True


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    cats = tax.get("categories", {})
    name_l = (name or "").lower()
    raw = " ".join([signature or "", snippet or ""])
    body = _strip_comments(raw)
    body_l = body.lower()
    file_l = (file or "").lower()

    # ── TWO-SIGNAL GATE (the FP backbone) ──
    # An item is accounting-sensitive ONLY with a domain signal AND a transition/arith signal in the BODY.
    # This is what stops the lens from tagging every function that merely says "credit" in a comment or
    # returns a stored config value.
    domain = has_domain_signal(body_l, tax)
    transition = has_transition_signal(body, tax)
    arith = _regex_any(body, tax.get("arithmetic_signals", []))
    signed = has_signed_unsigned(body, tax)
    oracle = has_oracle_scale(body_l, tax)

    # FP control: admin/config setter or pure upgrade-auth with no accounting transition → not tagged.
    if _any(body_l, _ADMIN_HINTS) and not transition:
        return _neg()

    # FP control: a simple stored-value getter is never accounting-sensitive (even if it names a ledger var).
    if _is_simple_getter(signature, body, tax):
        return _neg()

    if not domain:
        return _neg()
    if not (transition or arith or signed or oracle):
        return _neg()

    # ── category selection: need a BODY signal for the category, not just a name ──
    hr = set(tax.get("high_risk_categories", []))
    best = None
    for cat, meta in cats.items():
        nlen = _name_len(name_l, meta.get("name_patterns", []))
        file_hit = _any(file_l, [f.lower() for f in meta.get("file_patterns", [])])
        call_hit = _any(body_l, [c.lower() for c in meta.get("call_patterns", [])])
        sv_hit = _any(body_l, [s.lower() for s in meta.get("state_var_patterns", [])])
        arith_hit = _regex_any(body, meta.get("arithmetic_patterns", []))
        body_sig = call_hit or sv_hit or arith_hit
        if not body_sig:
            continue
        # Specificity ranking: a category whose OWN state var also participates in arithmetic (sv+arith) is
        # the most specific match (e.g. usdcAvailableForEngine += … → usdc_lockup, not a generic name match).
        sig_rank = 4 if (arith_hit and sv_hit) else 3 if arith_hit else 2 if sv_hit else 1
        key = (sig_rank, nlen, 1 if file_hit else 0, 1 if cat in hr else 0)
        matched_on = ("arith" if arith_hit else "state_var" if sv_hit else "call" if call_hit else "name")
        if best is None or key > best[0]:
            best = (key, cat, meta, matched_on)

    if best is None:
        return _neg()
    _, cat, meta, matched_on = best

    sig_head = (signature or "").split("{", 1)[0].lower()
    read_only = bool(re.search(r"\b(view|pure)\b", sig_head))
    domains = list(meta.get("accounting_domains", []))
    if signed and "signed_unsigned" not in domains:
        domains = domains + ["signed_unsigned"]
    if oracle and "oracle_scaled_values" not in domains:
        domains = domains + ["oracle_scaled_values"]

    return {
        "defi_accounting_sensitive": True, "category": cat,
        "accounting_domains": domains, "risk_tags": list(meta.get("risk_tags", [])),
        "review_hint": meta.get("review_hint", ""), "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
        "matched_on": matched_on,
        # public flags (also exposed underscore-prefixed for backwards-compat with is_high_risk)
        "signed_unsigned": signed, "oracle_scaled": oracle, "read_only": read_only,
        "_has_domain": domain, "_has_transition": transition or arith,
        "_signed_unsigned": signed, "_oracle_scaled": oracle, "_read_only": read_only,
    }


def _neg() -> dict:
    return {"defi_accounting_sensitive": False, "category": None, "accounting_domains": [], "risk_tags": [],
            "review_hint": "", "severity_ceiling_hint": None, "matched_on": None,
            "signed_unsigned": False, "oracle_scaled": False, "read_only": False,
            "_has_domain": False, "_has_transition": False, "_signed_unsigned": False,
            "_oracle_scaled": False, "_read_only": False}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    """High-risk = high-risk category AND the two-signal conservation shape: a domain signal AND a real
    state-transition/arith (or a signed/unsigned cast, or an oracle-scaled conversion) on accounting state.
    A read-only computed view can still be high-risk (e.g. getRealizedDebtUsd, getVaultCreditCapacity) because
    a wrong returned accounting value corrupts every downstream consumer — but a SIMPLE stored-value getter
    was already dropped by classify()."""
    tax = taxonomy or load_taxonomy()
    if not classification.get("defi_accounting_sensitive"):
        return False
    if classification.get("category") not in tax.get("high_risk_categories", []):
        return False
    if not classification.get("_has_domain"):
        return False
    return bool(classification.get("_has_transition") or classification.get("_signed_unsigned")
                or classification.get("_oracle_scaled"))
