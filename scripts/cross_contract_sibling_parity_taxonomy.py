#!/usr/bin/env python3
"""
cross_contract_sibling_parity_taxonomy.py — pure (no-I/O) classifier for the CROSS-CONTRACT sibling
parity research lens. Anchored on Size Credit M-06: BuyCreditMarket.validateBuyCreditMarket guards
`!creditPosition.forSale`; the sibling SellCreditMarket.validateSellCreditMarket reads the same
creditPosition but omits the forSale guard. Pairs sibling functions ACROSS contracts of the same module.

Reuses the Tier-1A machinery (scripts/sibling_function_parity_taxonomy): extract_features,
strip_comments, _is_wrapper. Adds cross-contract-specific extraction (guard fields, state-struct,
action verb, module dir) and classify_cross_pair.

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes.
"""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path

import sibling_function_parity_taxonomy as sfp  # reuse extract_features / strip_comments / _is_wrapper

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "cross_contract_sibling_parity_patterns.json"

_STATE_STRUCT = re.compile(r"\b([A-Z]\w*)\s+storage\s+\w+")
# predicate capture: require(...) bodies and if(...) guarding a revert/return
_REQUIRE_PRED = re.compile(r"\brequire\s*\(([^;]*?)\)\s*;", re.DOTALL)
_IF_REVERT_PRED = re.compile(r"\bif\s*\((.*?)\)\s*\{?\s*(?:revert|return)\b", re.DOTALL)
_DOTTED = re.compile(r"\.([A-Za-z_]\w*)")
_IDENT = re.compile(r"(?<![.\w])([A-Za-z_]\w*)")


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key, default):
    return _cfg().get(key, default)


def guard_fields(snippet: str) -> set:
    """Identifiers (esp. dotted fields) appearing inside require()/if(...)revert predicates."""
    body = sfp.strip_comments(snippet or "")
    preds = _REQUIRE_PRED.findall(body) + _IF_REVERT_PRED.findall(body)
    fields = set()
    for p in preds:
        for f in _DOTTED.findall(p):
            fields.add(f.lower())
        for f in _IDENT.findall(p):
            fields.add(f.lower())
    return fields


def state_struct(signature: str) -> str:
    m = _STATE_STRUCT.search(signature or "")
    return m.group(1) if m else ""


def action_verb(name: str) -> str:
    n = (name or "").lower().lstrip("_")
    for v in sorted(_t("action_verbs", []), key=len, reverse=True):
        if n.startswith(v) and len(n) > len(v):
            return v
    return ""


def extract_cross_features(name, signature="", modifiers=None, snippet="", visibility="", file="",
                           contract="") -> dict:
    feat = sfp.extract_features(name, signature, modifiers, snippet, visibility=visibility)
    feat["contract"] = contract
    feat["guard_fields"] = guard_fields(snippet)
    feat["state_struct"] = state_struct(signature)
    feat["verb"] = action_verb(name)
    feat["module_dir"] = os.path.dirname(file or "")
    feat.setdefault("own_calls", feat["calls"])
    feat.setdefault("own_ncalls", feat["_ncalls"])
    return feat


def _excluded(token: str) -> bool:
    if not token:
        return True
    if token[0].isupper():
        return True
    return token.lower() in set(_t("exclude_components", []))


def _component_type(token: str):
    tl = token.lower()
    for ptype, vocab in _t("components", {}).items():
        if any(v in tl for v in vocab):
            return ptype
    return None


def _is_eligibility(field: str) -> bool:
    vocab = _t("eligibility_guard_vocab", [])
    return any(v in field or field in v for v in vocab)


def _object_core(name: str) -> str:
    """Verb-stripped, antonym-stripped object token: validateBuyCreditMarket -> creditmarket."""
    n = (name or "").lower().lstrip("_")
    for v in sorted(_t("action_verbs", []), key=len, reverse=True):
        if n.startswith(v):
            n = n[len(v):]
            break
    for p in sorted(_t("antonym_prefixes", []), key=len, reverse=True):
        if n.startswith(p) and len(n) > len(p) + 3:
            n = n[len(p):]
            break
    return n


def _shared_object(a: str, b: str) -> bool:
    """True if the two verb/antonym-stripped object cores share a long-enough suffix or contain each
    other — i.e. the siblings operate on the SAME object (CreditMarket), not just the same verb."""
    ca, cb = _object_core(a), _object_core(b)
    if not ca or not cb:
        return False
    if ca == cb or ca in cb or cb in ca:
        return True
    # longest common suffix
    n = 0
    for x, y in zip(reversed(ca), reversed(cb)):
        if x != y:
            break
        n += 1
    return n >= _t("min_shared_object_suffix_len", 5)


def classify_cross_pair(fa: dict, fb: dict) -> list:
    """Return 0+ cross-contract parity candidates. Multi-gate: same verb, same module dir, shared
    state-struct, >=2 shared calls. fa/fb must carry the extract_cross_features fields."""
    # ---- multi-gate cross-sibling test ----
    if not fa.get("verb") or fa.get("verb") != fb.get("verb"):
        return []
    if _t("require_shared_state_struct", True):
        if not fa.get("state_struct") or fa.get("state_struct") != fb.get("state_struct"):
            return []
    if _t("require_same_module_dir", True) and fa.get("module_dir") != fb.get("module_dir"):
        return []
    if _t("require_shared_object_suffix", True) and not _shared_object(fa["name"], fb["name"]):
        return []
    shared = fa["calls"] & fb["calls"]
    if len(shared) < _t("min_shared_calls", 2):
        return []
    if sfp._is_wrapper(fa, fb) or sfp._is_wrapper(fb, fa):
        return []
    admin = set(_t("admin_modifiers", []))
    if (set(fa["modifiers"]) & admin) and (set(fb["modifiers"]) & admin):
        return []

    cands = []

    def emit_dir(strong, weak):
        if weak["visibility"] not in ("external", "public", ""):
            return
        weak_refs = set(weak["guard_fields"]) | {c.lower() for c in weak["calls"]}
        # (1) missing eligibility guard field (the M-06 shape) -> high
        elig_strong = {g for g in strong["guard_fields"] if _is_eligibility(g)}
        for g in sorted(elig_strong):
            if g in weak_refs or any(g in wr for wr in weak_refs):
                continue
            cands.append({
                "parity_type": "validation_parity", "missing_component": g, "missing_kind": "guard_field",
                "strong": strong["name"], "strong_contract": strong["contract"],
                "weak": weak["name"], "weak_contract": weak["contract"], "confidence": "high",
                "evidence": f"{strong['contract']}.{strong['name']} guards on `{g}`; "
                            f"{weak['contract']}.{weak['name']} operates on the same shared object "
                            f"(shared calls {sorted(shared)[:4]}) but omits the `{g}` guard",
                "signals": {"verb": strong["verb"], "state_struct": strong["state_struct"],
                            "module_dir": strong["module_dir"], "shared_calls": sorted(shared)[:8]},
            })
        # (2) missing controlled validator/recipient/cap call -> medium
        seen = {"validation_parity"} if cands else set()
        verbs = _t("action_verbs", [])
        only = {c for c in (strong["calls"] - weak["calls"]) if not _excluded(c) and c != weak["name"]}
        for tok in sorted(only):
            # skip sibling-validator self-calls (validateX/executeX) — these are not security components
            if any(tok.lower().startswith(v) for v in verbs):
                continue
            ptype = _component_type(tok)
            if not ptype or ptype in seen:
                continue
            seen.add(ptype)
            cands.append({
                "parity_type": ptype, "missing_component": tok, "missing_kind": "call",
                "strong": strong["name"], "strong_contract": strong["contract"],
                "weak": weak["name"], "weak_contract": weak["contract"], "confidence": "medium",
                "evidence": f"{strong['contract']}.{strong['name']} calls {tok} ({ptype}); "
                            f"{weak['contract']}.{weak['name']} omits it on a shared-subject path",
                "signals": {"verb": strong["verb"], "state_struct": strong["state_struct"],
                            "shared_calls": sorted(shared)[:8]},
            })

    emit_dir(fa, fb)
    emit_dir(fb, fa)
    seen, uniq = set(), []
    for c in cands:
        k = (c["parity_type"], c["weak_contract"], c["weak"], c["missing_component"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(c)
    return uniq
