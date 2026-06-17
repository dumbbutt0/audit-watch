#!/usr/bin/env python3
"""
math_estimator_taxonomy.py — Single source of truth for classifying MATH-ESTIMATOR / guard / formula
surfaces whose correctness depends on the INTENDED model (whitepaper / invariant), not on whether the
code matches its own NatSpec. Used by math_estimator_audit.py, validate_math_estimator_clears.py, and the
writer enforcement in coverage_sweep_write.py / deep_pass_write.py. Mirrors units_invariant_taxonomy.

Motivation (QuantAMM strict-eval H-11): the covariance estimator was strong-cleared because "formulas
match NatSpec" — yet the implementation deviated from the intended estimator. For math-heavy logic, code
agreeing with comments is NOT proof; the proof must independently re-derive the formula/invariant.

TWO-SIGNAL RULE (the false-positive backbone):
  math_estimator_sensitive := unambiguous_token
                              OR (strong_domain_term AND structural_signal)
                              OR (weak_domain_term  AND strong_structural_signal)
where
  strong_domain_term   = covariance/variance/gradient/momentum/moving-average/normalize/guard-rail/
                         epsilon/clamp/interpolat/estimator/invariant/ewma (estimator-class identity),
  weak_domain_term     = scale/precision/price/fee/oracle/multiplier/pack/lambda/kappa (generic), which
                         must co-occur with a STRONG signal (loop / matrix [i][j] / .pow/.log2/.exp2) to fire,
  structural_signal    = a loop, matrix/vector indexing, PRBMath .mul/.div/.pow/..., scale const, shift, clamp,
  unambiguous_token    = _guardQuantAMMWeights / _calculateQuantAMM* / _pow / calculateBlockNormalisedWeight.
This keeps lone constants, single +/- arithmetic, plain balance/transfer math, and pure getters OUT.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "math_estimator_patterns.json"

# estimator-class identity terms: a single structural signal is enough to make these sensitive.
_STRONG_TERMS = (
    "covariance", "covar", "variance", "gradient", "momentum", "moving average", "movingaverage",
    "ewma", "weighted average", "weightedaverage", "normalize", "normalise", "normalized weight",
    "normalizedweight", "guard rail", "guardrail", "guard-rail", "epsilon", "clamp", "interpolat",
    "estimator", "invariant", "rescale", "sd59x18",
)
# generic terms: require a STRONG structural signal (loop/matrix/pow) to avoid tagging precision one-liners.
_WEAK_TERMS = (
    "scale", "precision", "price", "fee", "uplift", "oracle", "multiplier", "pack", "unpack",
    "lambda", "kappa", "exponent", "matrix", "fixed-point", "fixed point", "prbmath",
)
_STRONG_SIGNALS = [
    r"for\s*\(", r"while\s*\(",
    r"\[\s*\w+\s*\]\s*\[\s*\w+\s*\]",
    r"\.pow\(", r"\.log2\(", r"\.exp2\(", r"\.sqrt\(",
]
# Economic-shift routing: a Solidity bit shift (<< / >>) is value-SCALING (not bitmap/flag twiddling)
# when an economic term sits next to it. `2 << difficulty` (getFee) must route to math review; `1 << index`
# / `flags << roleId` / packed-storage shifts must NOT, unless an economic term ties the shift to value
# movement. Shifts are far rarer than loops, so this gate (shift + economic term − bitmask context) is
# tight enough to bypass the dom!="other" guard the weak-term branch uses.
_ECONOMIC_TERMS = frozenset({
    "fee", "price", "rate", "reward", "penalty", "score", "difficulty", "weight", "multiplier",
    "shares", "supply", "debt", "collateral", "balance", "amount", "liquidity", "reserve", "index",
    "ratio", "quorum", "threshold", "gas", "premium", "discount", "slippage", "interest", "yield",
})
# Bitmask / packing / permission context: a shift here is bit twiddling, not value scaling — suppress.
_BITMASK_CONTEXT_TERMS = frozenset({
    "bitmap", "bitset", "bitfield", "bitmask", "mask", "flag", "flags", "permission", "permissions",
    "role", "roles", "packed", "pack", "unpack", "encode", "decode", "bitwise", "slot", "offset",
})
_SHIFT_RE = re.compile(r"<<|>>")
# the `1 << x` set-a-bit idiom (also `1<<x`), which is a bitmap/flag, not scaling like `2 << difficulty`.
_BITMASK_SHIFT_RE = re.compile(r"\b1\s*<<\s*\w")
_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_FILE_CACHE: dict[str, list[str]] = {}


def _tokens(text: str) -> set[str]:
    """camelCase-split → lowercase → alpha tokens (so rewardMultiplier → {reward, multiplier})."""
    return set(re.findall(r"[a-z]+", _CAMEL_RE.sub(" ", text or "").lower()))


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"domain_terms": [], "structural_signals": [], "unambiguous_tokens": [],
                "high_risk_domains": [], "domains": {}}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def _regex_any(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        try:
            if re.search(p, text, re.IGNORECASE):
                return True
        except re.error:
            continue
    return False


def _neg() -> dict:
    return {"math_estimator_sensitive": False, "math_domain": None, "risk_tags": [],
            "review_hint": "", "severity_ceiling_hint": None, "matched_on": None}


def _pick_domain(name_l: str, body_l: str, tax: dict) -> tuple[str, dict]:
    """Choose the most specific math_domain: name_pattern match > term-in-name > term-in-body > other."""
    domains = tax.get("domains", {})
    best = None  # (rank, domain, meta)
    for dom, meta in domains.items():
        if dom == "other":
            continue
        nm_hit = any(p.lower() in name_l for p in meta.get("name_patterns", []))
        term_name = any(t in name_l for t in meta.get("terms", []))
        term_body = any(t in body_l for t in meta.get("terms", []))
        if nm_hit:
            rank = 3
        elif term_name:
            rank = 2
        elif term_body:
            rank = 1
        else:
            continue
        if best is None or rank > best[0]:
            best = (rank, dom, meta)
    if best is None:
        return "other", domains.get("other", {})
    return best[1], best[2]


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None, title: str = "") -> dict:
    tax = taxonomy or load_taxonomy()
    name_l = (name or "").lower()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    body_l = body.lower()
    ident = name_l + " " + body_l  # domain terms only matched against the function's own identity/body

    unamb = [t.lower() for t in tax.get("unambiguous_tokens", [])]
    if any(t in name_l or t in body_l for t in unamb):
        dom, meta = _pick_domain(name_l, body_l, tax)
        return {"math_estimator_sensitive": True, "math_domain": dom,
                "risk_tags": list(meta.get("risk_tags", [])), "review_hint": meta.get("review_hint", ""),
                "severity_ceiling_hint": meta.get("severity_ceiling_hint"), "matched_on": "unambiguous"}

    signals = tax.get("structural_signals", [])
    has_signal = _regex_any(body, signals)
    has_strong_signal = _regex_any(body, _STRONG_SIGNALS)
    has_strong_term = any(t in ident for t in _STRONG_TERMS)
    has_weak_term = any(t in ident for t in _WEAK_TERMS)

    dom, meta = _pick_domain(name_l, body_l, tax)

    # economic-shift: a bit shift used for VALUE SCALING (economic term nearby, not bitmap/flag context).
    # econ_text includes the RAW snippet (comments included) + tags + title — routing to review is a recall
    # decision, not a severity decision, so reading comments here is allowed.
    econ_text = " ".join([name or "", signature or "", snippet or "", title or "",
                          " ".join(tags or [])])
    token_set = _tokens(econ_text)
    has_shift = bool(_SHIFT_RE.search(body))
    bitmask_context = bool(token_set & _BITMASK_CONTEXT_TERMS) or bool(_BITMASK_SHIFT_RE.search(body))
    economic_shift = has_shift and bool(token_set & _ECONOMIC_TERMS) and not bitmask_context

    # strong (estimator-class) term + any structural signal → sensitive (domain may be 'other', e.g. a
    # bare 'estimator'/'invariant' helper). A generic WEAK term (price/fee/scale/pack/...) only fires with
    # a STRONG signal AND only when it resolves to a recognized math domain — this keeps loop-bearing
    # getters / string helpers (domain 'other') OUT (FP control). economic_shift is its own gated branch.
    sensitive = ((has_strong_term and has_signal)
                 or (has_weak_term and has_strong_signal and dom != "other")
                 or economic_shift)
    if not sensitive:
        return _neg()

    matched_on = ("strong_term" if has_strong_term and has_signal
                  else "weak_term+strong_signal" if (has_weak_term and has_strong_signal and dom != "other")
                  else "economic_shift")
    return {"math_estimator_sensitive": True, "math_domain": dom,
            "risk_tags": list(meta.get("risk_tags", [])), "review_hint": meta.get("review_hint", ""),
            "severity_ceiling_hint": meta.get("severity_ceiling_hint"), "matched_on": matched_on}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    tax = taxonomy or load_taxonomy()
    if not classification.get("math_estimator_sensitive"):
        return False
    return classification.get("math_domain") in tax.get("high_risk_domains", [])


def _snippet(file_rel: str, start, end) -> str:
    """Read a source span (mirrors units_invariant_audit._snippet); relative to ROOT."""
    if not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    if not lines:
        return ""
    a = max(0, int(start) - 1)
    b = min(len(lines), int(end or start))
    return "\n".join(lines[a:b])[:4000]


def classify_manifest_item(item: dict, taxonomy: dict | None = None) -> dict:
    """Classify a coverage-manifest item, reading its source span for the snippet. Used by the lens,
    the validator, and the writer enforcement so all three agree on what is math-estimator-sensitive."""
    span = item.get("source_span", {}) or {}
    snip = _snippet(item.get("file", ""), span.get("start_line"), span.get("end_line"))
    return classify(item.get("name", ""), item.get("signature", ""), item.get("file", ""),
                    item.get("contract", ""), snippet=snip, tags=item.get("tags"), taxonomy=taxonomy)
