#!/usr/bin/env python3
"""
getter_state_taxonomy.py — Single source of truth for classifying getter-vs-state reconciliation
surfaces. Used by getter_state_audit.py. Mirrors units_invariant_taxonomy / migration_flow_taxonomy.

This is NOT a generic view-function scanner. A getter/helper is dangerous only when the SHAPE, ORDERING,
FRESHNESS, ENCODING, or BRANCHING of its return value can be wrong AND a consumer trusts it. The signal
lives in the function BODY (snippet), so the detector passes a source snippet and classify() looks at
name + signature + snippet + mutability + consumer linkage.

FP backbone (three gates, all required):
  getter_state_sensitive := has_getter_context AND has_strong_feature AND category_signal
where
  has_getter_context = view/pure mutability, or a getter_context_terms word in name/snippet, or a
                       decode/encode/abi/sort/calldata token in the body;
  has_strong_feature = >=1 of {transformed_return, multi_return, abi, struct_token, calldata_offset,
                       array_alloc, array_index, sorting_or_compare, branch_return, cache_storage}.
                       A bare `return s.x` getter, a constant-returning view, and a plain storage read
                       have NO strong feature -> excluded. (consumer-dependency alone is NOT strong.)
  category_signal    = a category's SPECIFIC call/return/state-read/abi pattern matches the body
                       (generic `s.` is deliberately NOT a signal); two feature-derived categories
                       (view_used_by_state_path, pure_helper_control_flow) may instead be selected
                       from the feature set, but only on top of has_strong_feature.
Names only pick the category; they are never a trigger.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "getter_state_patterns.json"

# pure math/helper libraries already owned by the units lens — not getter/state bugs on their own
_PURE_MATH_HINTS = ("mulmod", "addmod", "sqrt", "log2", "exp2", "mostsignificantbit", "muldiv", "_mul", "pow")

_RETURN_RE = re.compile(r"return\s+([^;]+);")
_STRONG = {"transformed_return", "multi_return", "abi", "struct_token", "calldata_offset",
           "array_alloc", "array_index", "sorting_or_compare", "branch_return", "cache_storage"}


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"categories": {}, "getter_context_terms": [], "high_risk_categories": []}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


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


def _is_regexy(p: str) -> bool:
    return bool(re.search(r"[\\\[\](){}^$|?*+]", p))


def _signal_hit(body_l: str, body: str, meta: dict) -> bool:
    pats = (meta.get("call_patterns", []) + meta.get("return_patterns", [])
            + meta.get("state_read_patterns", []) + meta.get("abi_patterns", []))
    subs = [p for p in pats if not _is_regexy(p)]
    rxs = [p for p in pats if _is_regexy(p)]
    return _matches(body_l, [s.lower() for s in subs]) or _regex_any(body, rxs)


def _name_len(name_l: str, patterns: list[str]) -> int:
    best = 0
    for p in patterns:
        pl = p.lower()
        if pl and pl in name_l:
            best = max(best, len(pl))
    return best


def _state_reads(body: str) -> list[str]:
    reads = set(re.findall(r"\bs\.[A-Za-z_][\w.]*", body))
    reads |= set(re.findall(r"\b\w*Storage\(\)\.[A-Za-z_][\w.]*", body))
    reads |= set(re.findall(r"\bblueprint\w*\b|\bpublisherCounter\b|\bblock\.timestamp\b", body))
    return sorted(reads)[:8]


def _features(name_l: str, signature: str, body: str, mutability: str, consumed_by_state: bool) -> set[str]:
    feats: set[str] = set()
    rets = _RETURN_RE.findall(body)
    for r in rets:
        rs = r.strip()
        if re.search(r"[+\-*/%]|\babi\.(en|de)code|\b\w+\([^)]*\)|\.\w+\([^)]*\)", rs):
            feats.add("transformed_return")
        if "[" in rs:
            feats.add("array_index")
    if any("," in r for r in rets):
        feats.add("multi_return")
    sigret = re.search(r"returns\s*\(([^)]*)\)", signature or "")
    if sigret and "," in sigret.group(1):
        feats.add("multi_return")
    # for/while loop accumulation = a transformed/aggregated return (e.g. totalDeltaB summation)
    if re.search(r"\b(for|while)\s*\(", body) and re.search(r"\.add\(|\.sub\(|\+=|-=", body):
        feats.add("transformed_return")
    if re.search(r"abi\.(decode|encode|encodePacked|encodeWithSelector)", body):
        feats.add("abi")
    if re.search(r"AdvancedPipeCall|AdvancedFarmCall|PipeCall", body):
        feats.add("struct_token")
    if re.search(r"\bcalldataload\b|\.offset\b|\bmload\(|\bmstore\(|pasteBytes|pasteAdvancedBytes", body):
        feats.add("calldata_offset")
    if re.search(r"new\s+\w[\w\.]*\[\]\(|\.length\s*(==|!=|<|>)", body):
        feats.add("array_alloc")
    if re.search(r"\bquickSort\b|\bsort\(|\bswap\(|\bpivot\b", body, re.IGNORECASE):
        feats.add("sorting_or_compare")
    if re.search(r"if\s*\([^)]*[<>]=?[^)]*\)\s*\{?\s*return", body):
        feats.add("branch_return")
    if re.search(r"=\s*s\.", body) and len(re.findall(r"\bs\.", body)) >= 2:
        feats.add("cache_storage")
    if consumed_by_state and mutability in ("view", "pure"):
        feats.add("consumer_dep")
    return feats


def _return_shape(feats: set[str]) -> str:
    if "abi" in feats or "struct_token" in feats:
        return "abi_encoded"
    if "branch_return" in feats:
        return "branched_default"
    if "array_index" in feats or "array_alloc" in feats:
        return "struct_or_array"
    if "multi_return" in feats:
        return "multi_field"
    if "transformed_return" in feats:
        return "transformed"
    if "cache_storage" in feats:
        return "cached_local"
    return "single_var"


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", mutability: str = "", tags=None, consumed_by_state: bool = False,
             taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    cats = tax.get("categories", {})
    terms = [t.lower() for t in tax.get("getter_context_terms", [])]
    name_l = (name or "").lower()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    body_l = body.lower()
    hay = " ".join([name_l, body_l, (file or "").lower(), (contract or "").lower(),
                    " ".join(tags or []).lower()])

    # units owns pure math helpers, UNLESS they do ordering/control flow (sorting/swap/branch).
    if any(h in name_l for h in _PURE_MATH_HINTS) and not re.search(r"sort|swap|\bif\s*\(", body_l):
        return _neg()

    has_ctx = (mutability in ("view", "pure")) or any(t in hay for t in terms) \
        or bool(re.search(r"abi\.(en|de)code|decode|encode|sort|clipboard|calldataload", body_l))
    if not has_ctx:
        return _neg()

    feats = _features(name_l, signature, body, mutability, consumed_by_state)
    if not (feats & _STRONG):
        return _neg()                       # required STRONG structural-feature gate

    hr = set(tax.get("high_risk_categories", []))
    best = None
    for cat, meta in cats.items():
        signal = _signal_hit(body_l, body, meta)
        # view_used_by_state_path is a catch-all for views consumed by a state path, but only when the
        # return is NOTABLY shaped (branch/tuple/abi/struct/sorting) — not for every view that merely
        # returns a computed value. This keeps the lens precise on a large manifest.
        _NOTABLE = {"branch_return", "multi_return", "abi", "struct_token", "sorting_or_compare"}
        feature_only = (
            (cat == "view_used_by_state_path" and "consumer_dep" in feats and bool(feats & _NOTABLE))
            or (cat == "pure_helper_control_flow" and "branch_return" in feats
                and mutability in ("pure", "internal", ""))
        )
        if not (signal or feature_only):
            continue
        nlen = _name_len(name_l, meta.get("name_patterns", []))
        spec = meta.get("specificity", 1)
        key = (spec, 1 if signal else 0, nlen, 1 if cat in hr else 0)
        if best is None or key > best[0]:
            best = (key, cat, meta, ("signal" if signal else "feature"))

    if best is None:
        return _neg()
    _, cat, meta, matched_on = best
    consumer_hint = ("consumed_by_state_path" if consumed_by_state
                     else ("state_fn" if mutability not in ("view", "pure", "") else "view_only"))
    return {
        "getter_state_sensitive": True,
        "category": cat,
        "risk_tags": list(meta.get("risk_tags", [])),
        "state_reads": _state_reads(body),
        "return_shape": _return_shape(feats),
        "consumer_hint": consumer_hint,
        "review_hint": meta.get("review_hint", ""),
        "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
        "matched_on": matched_on,
        "features": sorted(feats),
    }


def _neg() -> dict:
    return {"getter_state_sensitive": False, "category": None, "risk_tags": [], "state_reads": [],
            "return_shape": None, "consumer_hint": None, "review_hint": "",
            "severity_ceiling_hint": None, "matched_on": None, "features": []}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    tax = taxonomy or load_taxonomy()
    if not classification.get("getter_state_sensitive"):
        return False
    return classification.get("category") in tax.get("high_risk_categories", [])
