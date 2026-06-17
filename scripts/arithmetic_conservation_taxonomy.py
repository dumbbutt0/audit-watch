#!/usr/bin/env python3
"""
arithmetic_conservation_taxonomy.py — pure (no-I/O) classifier for ARITHMETIC-CONSERVATION surfaces:
functions whose correctness depends on a conservation invariant that the attack-surface scorer gives no
credit to, so they score low and get thin-cleared. Used by arithmetic_conservation_audit.py (detector) and
its tests. Mirrors math_estimator_taxonomy / abi_getter_mismatch_taxonomy (pure, testable core).

Motivation (Blackhole 2025-05 generalization eval, cross-eval-confirmed vs QuantAMM/Silo/Hybra):
  - M-01 MinterUpgradeable.calculate_rebase (score 2): `veBlackSupply = _veTotal + _smNFTBalance +
    _superMassiveBonus` where `_veTotal = black.balanceOf(_ve)` already includes smNFT -> double-count.
  - M-06 Pair._k (score 0): stable product invariant `(_x*_y)/1e18 * (_x*_x/1e18 + _y*_y/1e18)/1e18`
    rounds to zero for tiny inputs -> first-LP DoS.

TWO-SIGNAL RULE (the false-positive backbone) — a function is conservation-sensitive iff EITHER shape fires:

  Shape 1 "supply_aggregate" (double-count) := A AND B
    A (aggregate)   = an assignment/return RHS combines >=2 distinct identifier terms with + / - .
    B (provenance)  = a balanceOf()/totalSupply() call is present, OR an aggregate LHS/return name or a
                      term matches a supply/balance token (supply/totalSupply/circulating/balance/total).
    confidence high if the aggregate name itself is supply/total/circulating, else medium.

  Shape 2 "invariant_rounding" (floor-to-zero) := C1 AND C2
    C1 (product/invariant) = an invariant-token name (_k / k / invariant) OR >=2 multiplications between
                             identifiers in the body.
    C2 (floor hazard)      = an integer division `/` between identifiers/constants is present.
    confidence medium (looser shape; overlaps math_estimator -> the AUDIT de-dups against it).

This keeps lone constants, single +/- of one term, plain transfer math, generic single-mult pricing, and
pure getters OUT. `view`/`pure` are KEPT (M-01 is `public view`).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "arithmetic_conservation_patterns.json"

ROUTED_CONFIDENCE = frozenset({"high", "medium"})


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


# --- token sets (config-overridable) ---
def _supply_tokens() -> tuple:
    # naming tokens that ESCALATE a balanceOf/totalSupply aggregate to high confidence. Deliberately tight
    # (no bare "total"/"balance" — those over-match setters/transfers); the balanceOf/totalSupply CALL is
    # the mandatory provenance, this just names the canonical supply-aggregate surface.
    return tuple(_cfg().get("supply_tokens", ["supply", "totalsupply", "circulating", "circsupply"]))


def _invariant_name_tokens() -> tuple:
    # shape-2 is NAME-ANCHORED to curve/invariant helpers (precise); generic product/division math is
    # math_estimator's job and is de-duped by the audit.
    return tuple(_cfg().get("invariant_name_tokens", ["_k", "invariant", "curve", "_get_y"]))


# --- regexes ---
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
# an assignment / return whose RHS is >=2 identifier-ish terms joined by + or - .
# a term is an identifier with optional member access / call args, e.g. a, _x, foo.bar, foo(...)
_TERM = r"[A-Za-z_]\w*(?:\s*\.\s*\w+)*(?:\s*\([^;{}]*\))?"
_BAL_CALL_RE = re.compile(r"\.\s*(?:balanceOf|totalSupply)\s*\(")
# multiplication between two identifier/number operands (not `**`, not `*/` comment-end)
_MUL_RE = re.compile(r"[A-Za-z0-9_)\]]\s*\*\s*(?!\*)[A-Za-z0-9_(]")
# integer division between two identifier/number operands (not `//`)
_DIV_RE = re.compile(r"[A-Za-z0-9_)\]]\s*/\s*(?!/)[A-Za-z0-9_(]")
_IDENT_RE = re.compile(r"[A-Za-z_]\w*")
_ARITH_OP_RE = re.compile(r"[+\-*/]")
# the LHS name of an `[type] NAME = ...;` assignment, or `return` for a bare return
_LHS_NAME_RE = re.compile(r"(?:^|[;{])\s*(?:[A-Za-z_][\w\[\]]*\s+)*([A-Za-z_]\w*)\s*=\s*(" + _TERM + r"(?:\s*[+\-]\s*" + _TERM + r")+)\s*;", re.M)


def _strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _name_matches(name: str, tokens) -> bool:
    n = (name or "").lower()
    return any(t in n for t in tokens)


def _is_pure_getter(body: str) -> bool:
    """A body that is essentially a single `return storageVar;` (no arithmetic) — never sensitive."""
    b = _strip_comments(body)
    inner = b[b.find("{") + 1:b.rfind("}")] if "{" in b and "}" in b else b
    inner = inner.strip()
    if not _ARITH_OP_RE.search(inner):
        return True
    return False


def _named_aggregates(body: str) -> list[tuple[str, str]]:
    """(lhs_name, rhs) for `[type] NAME = <>=2 terms>;` assignments, EXCLUDING accumulators where the LHS
    name also appears as a RHS term (e.g. `total = total + a`) — those are accumulation, not a conservation
    aggregate. M-01's `veBlackSupply = _veTotal + _smNFTBalance + bonus` survives (LHS not in RHS)."""
    out = []
    for m in _LHS_NAME_RE.finditer(body):
        lhs, rhs = m.group(1), m.group(2)
        if lhs in set(_IDENT_RE.findall(rhs)):
            continue
        out.append((lhs, rhs.strip()))
    return out


def _return_aggregates(body: str) -> list[str]:
    """`return <>=2 terms>;` aggregate expressions (no LHS — always a genuine aggregate)."""
    return [m.group(1).strip() for m in
            re.finditer(r"\breturn\s+(" + _TERM + r"(?:\s*[+\-]\s*" + _TERM + r")+)\s*;", body)]


def _aggregates(body: str) -> list[str]:
    """All surviving aggregate RHS expressions (named non-accumulators + returns)."""
    return [rhs for _, rhs in _named_aggregates(body)] + _return_aggregates(body)


def _aggregate_names(body: str) -> list[str]:
    """LHS names of surviving aggregate assignments (for confidence)."""
    return [lhs for lhs, _ in _named_aggregates(body)]


def classify(name: str, signature: str, file: str, contract: str,
             snippet: str = "", tags=None) -> dict:
    """Return {sensitive, shape, signals, confidence, terms, reason}. Pure; snippet is the function body."""
    neg = {"sensitive": False, "shape": None, "signals": [], "confidence": None, "terms": [], "reason": ""}
    body = _strip_comments(snippet or "")
    if not body.strip():
        return neg
    if _is_pure_getter(snippet or ""):
        return neg

    supply_tokens = _supply_tokens()

    # ---- Shape 1: supply/balance aggregate double-count (A AND B) ----
    # A = >=2-term aggregate (non-accumulator). B = a balanceOf()/totalSupply() CALL is present (the
    # mandatory provenance — the M-01 double-count exists precisely because a balanceOf-derived total
    # already includes a term that is then added again). A supply/circulating-named aggregate escalates to
    # high. Requiring the call keeps setters/transfers/plain arithmetic OUT.
    aggs = _aggregates(body)
    has_bal_call = bool(_BAL_CALL_RE.search(body))
    if aggs and has_bal_call:
        agg_names = _aggregate_names(body)
        name_hit = any(_name_matches(n, supply_tokens) for n in agg_names) or \
            any(_name_matches(t, supply_tokens) for agg in aggs for t in _IDENT_RE.findall(agg))
        conf = "high" if name_hit else "medium"
        signals = ["aggregate_ge2_terms", "balanceof_or_totalsupply_call"]
        if name_hit:
            signals.append("supply_named")
        return {
            "sensitive": True, "shape": "supply_aggregate", "signals": signals,
            "confidence": conf, "terms": agg_names[:6] or aggs[:3],
            "reason": (f"{name} combines >=2 terms into an aggregate "
                       f"({', '.join(agg_names[:3]) or aggs[0][:60]}) alongside a balanceOf/totalSupply read "
                       f"-> double-count / conservation risk; verify no term is already included in another"),
        }

    # ---- Shape 2: product/invariant rounding-to-zero (C1 AND C2), NAME-ANCHORED ----
    # C1 = the function NAME is a curve/invariant helper (_k / invariant / curve / _get_y). C2 = a product
    # AND an integer division are present. Generic product/division math (Math.sqrt, pricing, etc.) is NOT
    # name-anchored -> excluded here; math_estimator owns it and the audit de-dups.
    n_mul = len(_MUL_RE.findall(body))
    has_div = bool(_DIV_RE.search(body))
    invariant_name = _name_matches(name, _invariant_name_tokens())
    if invariant_name and has_div and (n_mul >= 1):
        return {
            "sensitive": True, "shape": "invariant_rounding", "signals": ["product_invariant", "integer_division"],
            "confidence": "medium", "terms": [],
            "reason": (f"{name} computes a product-style invariant with integer division "
                       f"({n_mul} mul, division present) -> floor-to-zero rounding risk for small inputs; "
                       f"verify the minimum-input rounding behavior and any zero/min guard"),
        }

    return neg
