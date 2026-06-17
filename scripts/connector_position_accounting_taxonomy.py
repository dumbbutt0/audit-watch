#!/usr/bin/env python3
"""
connector_position_accounting_taxonomy.py — pure (no-I/O) classifier for CONNECTOR / TVL / POSITION-ACCOUNTING
surfaces whose value is computed from EXTERNAL protocol state (proxy readers, markets, position managers,
registry keys) — the class the NOYA 2024-04 eval proved the existing lenses miss. Self-contained: it copies
the small pure helpers it needs from arithmetic_conservation_taxonomy (which stays frozen/untouched).

Narrow first slice — three NAME-GATED, two-signal shapes (the eval's tractable misses):

  Shape A "external_reader_aggregate" (NOYA H-11 SNX, H-19 MorphoBlue) := TVL/value-named fn AND a >=2-term
    +/- aggregate (anywhere, incl. inside a call arg) AND >=1 term sourced from an EXTERNAL position-reader
    call (getAccountCollateral / market( / position( / idToMarketParams / toAssets* / getReserves / ...).
    high if the aggregate mixes a debt/borrow term with supply/collateral (sign error / double-count), else medium.
      H-11: `_getValue(.., totalDeposited + totalAssigned)` from getAccountCollateral (assigned⊆deposited).
      H-19: `supplyAmount + borrowAmount + collateral` from market()/position()/toAssetsUp (borrow is a liability).

  Shape B "position_tvl_product_div" (NOYA H-13 Balancer) := TVL/value-named fn AND a product (*) AND a
    division (/) with NO >=2-term aggregate, especially dividing by a weight/supply/totalSupply term. medium.
      H-13: `1e18*token1bal*lpBalance/_weight/_totalSupply` (already weight-adjusted -> double-divide).

  Shape C "registry_key_mismatch" (NOYA H-12 Registry.updateHoldingPosition) := registry-named fn AND the
    position key is derived BOTH from msg.sender (owner) AND from `.calculatorConnector` -> inconsistent
    position-key identity (store-key vs read-key). medium.

Deferred (NOT here — need a semantic/completeness model, high FP risk): TVL that OMITS a staked balance
(H-06), "assumes ownership of all tick liquidity" (H-20).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "connector_position_accounting_patterns.json"

ROUTED_CONFIDENCE = frozenset({"high", "medium"})


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


# --- config-overridable token sets ---
def _tvl_names() -> tuple:
    return tuple(_cfg().get("tvl_value_names",
                ["_getpositiontvl", "getpositiontvl", "positiontvl", "gettvl", "getvalue", "_getvalue", "updatetvl"]))


def _registry_names() -> tuple:
    return tuple(_cfg().get("registry_names",
                ["updateholdingposition", "holdingpositionid", "calculatepositionid", "removeholdingposition"]))


def _external_reader_calls() -> tuple:
    return tuple(_cfg().get("external_reader_calls",
                ["getAccountCollateral", "getAccount", "idToMarketParams", "toAssetsUp", "toAssets",
                 "getReserves", "getPoolTokens", "getUserAccountData", "getCollateral", "position", "market"]))


def _debt_tokens() -> tuple:
    return tuple(_cfg().get("debt_tokens", ["borrow", "debt", "owed", "liabilit"]))


def _div_risk_tokens() -> tuple:
    return tuple(_cfg().get("div_risk_tokens", ["weight", "supply", "totalsupply"]))


# --- regexes (copied from arithmetic_conservation_taxonomy; this lens does not import-mutate it) ---
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
_TERM = r"[A-Za-z_]\w*(?:\s*\.\s*\w+)*(?:\s*\([^;{}]*\))?"
# any >=2-term +/- run anywhere in the body (incl. inside a call arg like `_getValue(.., a + b)`)
_ANY_AGG_RE = re.compile(_TERM + r"(?:\s*[+\-]\s*" + _TERM + r"){1,}")
_MUL_RE = re.compile(r"[A-Za-z0-9_)\]]\s*\*\s*(?!\*)[A-Za-z0-9_(]")
_DIV_RE = re.compile(r"[A-Za-z0-9_)\]]\s*/\s*(?!/)[A-Za-z0-9_(]")
_IDENT_RE = re.compile(r"[A-Za-z_]\w*")
_ARITH_OP_RE = re.compile(r"[+\-*/]")
# position key derived from msg.sender vs from a .calculatorConnector field
_MSGSENDER_KEY_RE = re.compile(r"abi\.encode\(\s*msg\.sender")
_CALC_KEY_RE = re.compile(r"\.\s*calculatorConnector")


def _strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _name_has(name: str, tokens) -> bool:
    n = (name or "").lower()
    return any(t in n for t in tokens)


def _body_has_reader(body: str, readers) -> list[str]:
    hits = []
    for r in readers:
        if re.search(r"\.\s*" + re.escape(r) + r"\s*\(", body) or re.search(r"\b" + re.escape(r) + r"\s*\(", body):
            hits.append(r)
    return hits


def _aggregate_runs(body: str) -> list[str]:
    """All >=2-term +/- runs anywhere (incl. call args). Excludes a pure self-accumulator `x = x + a`."""
    out = []
    for m in _ANY_AGG_RE.finditer(body):
        run = m.group(0).strip()
        ids = _IDENT_RE.findall(run)
        # drop a 2-term run that is just `x <op> x` style accumulation handled elsewhere — keep distinct terms
        if len(set(ids)) >= 2:
            out.append(run)
    return out


def classify(name: str, signature: str, file: str, contract: str,
             snippet: str = "", tags=None) -> dict:
    """Return {sensitive, shape, signals, confidence, terms, reason}. Pure; snippet is the function body."""
    neg = {"sensitive": False, "shape": None, "signals": [], "confidence": None, "terms": [], "reason": ""}
    body = _strip_comments(snippet or "")
    if not body.strip():
        return neg

    is_tvl = _name_has(name, _tvl_names())
    is_registry = _name_has(name, _registry_names())
    if not (is_tvl or is_registry):
        return neg                                  # NAME-GATE: the primary FP control

    # ---- Shape C: registry position-key identity mismatch (H-12) ----
    if is_registry:
        msgsender_key = bool(_MSGSENDER_KEY_RE.search(body))
        calc_key = bool(_CALC_KEY_RE.search(body))
        if msgsender_key and calc_key:
            return {
                "sensitive": True, "shape": "registry_key_mismatch",
                "signals": ["msg_sender_keyed_position", "calculatorConnector_keyed_position"],
                "confidence": "medium", "terms": ["msg.sender", "calculatorConnector"],
                "reason": (f"{name} derives the holding-position key from BOTH msg.sender (owner) and "
                           f".calculatorConnector — inconsistent position-key identity on store vs read; "
                           f"verify the remove/update path keys isPositionUsed with the same connector as creation"),
            }
        return neg

    # ---- TVL/value-named: Shape A then Shape B ----
    if _ARITH_OP_RE.search(body) is None:
        return neg                                  # pure getter / no arithmetic

    readers = _body_has_reader(body, _external_reader_calls())
    aggs = _aggregate_runs(body)

    # Shape A — external-reader position aggregate (H-11, H-19)
    if aggs and readers:
        agg_blob = " ".join(aggs).lower()
        has_debt = any(t in agg_blob for t in _debt_tokens())
        conf = "high" if has_debt else "medium"
        signals = ["tvl_aggregate_ge2_terms", "external_position_reader"]
        if has_debt:
            signals.append("debt_mixed_with_asset")
        return {
            "sensitive": True, "shape": "external_reader_aggregate", "signals": signals,
            "confidence": conf, "terms": aggs[:4],
            "reason": (f"{name} sums >=2 position terms ({aggs[0][:60]}) sourced from external reader(s) "
                       f"{readers[:3]} -> double-count / sign (debt-as-asset) / omission risk; "
                       f"enumerate each term, its reader, and asset-vs-liability sign"),
        }

    # Shape B — PositionTVL product/division miscalc (H-13)
    n_mul = len(_MUL_RE.findall(body))
    has_div = bool(_DIV_RE.search(body))
    if n_mul >= 1 and has_div and not aggs:
        div_risk = any(t in body.lower() for t in _div_risk_tokens())
        signals = ["tvl_product_division"]
        if div_risk:
            signals.append("divide_by_weight_or_supply")
        return {
            "sensitive": True, "shape": "position_tvl_product_div",
            "signals": signals, "confidence": "medium", "terms": [],
            "reason": (f"{name} computes TVL via a product/division chain ({n_mul} mul + division"
                       f"{', divides by weight/supply' if div_risk else ''}) -> miscalc risk "
                       f"(e.g. dividing an already-weight-adjusted balance again); re-derive the formula"),
        }

    return neg
