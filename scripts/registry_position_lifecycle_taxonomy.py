#!/usr/bin/env python3
"""
registry_position_lifecycle_taxonomy.py — pure (no-I/O) classifier for the REGISTRY / POSITION-LIFECYCLE
research lens. Detects position-registry desyncs:
  Shape 1 `missing_registry_update` (NOYA H-23): a function mutates the same position SUBJECT (a proxy/
    manager object) via a LIFECYCLE-verb method that its registry-updating siblings also mutate, but omits
    the registry update they perform.
  Shape 2 `unguarded_registry_remove` (NOYA H-18): a function performs a registry REMOVE without the
    emptiness guard a sibling remove on the same registry carries.

DISTINCT from connector_position_accounting Shape C (single-function key mismatch / H-12 — not flagged here)
and from sibling_function_parity (name/call kinship). Reuses sibling_function_parity_taxonomy.strip_comments.

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import sibling_function_parity_taxonomy as sfp

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "registry_position_lifecycle_patterns.json"

_OBJ_METH = re.compile(r"([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*\(")
_REG_OBJS = {"registry", "this", "msg", "address"}
_REMOVE_FLAG = re.compile(r",\s*true\s*\)", re.DOTALL)


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key, default):
    return _cfg().get(key, default)


def _has_lifecycle_verb(method: str) -> bool:
    m = method.lower()
    if any(v in m for v in _t("lifecycle_verbs", [])):
        # exclude when the lifecycle hit is actually an amount-only verb prefix
        return True
    return False


def _is_amount_only(method: str) -> bool:
    m = method.lower()
    return any(m.startswith(v) or v in m for v in _t("amount_only_verbs", []))


def extract_registry_features(name, signature="", snippet="", visibility="", mutability="") -> dict:
    body = sfp.strip_comments(snippet or "")
    blow = body.lower()
    obj_meth = {(o.lower(), m.lower()) for o, m in _OBJ_METH.findall(body)}
    reg_vocab = _t("registry_mutation_vocab", [])
    # a registry-mutation call: method (or obj.method) matches the vocab
    reg_calls = {(o, m) for (o, m) in obj_meth if any(v in m for v in reg_vocab)}
    has_reg = bool(reg_calls)
    # subject (proxy) calls: obj.method where obj is not registry/this and method is a state-mutating verb
    subj_calls = {(o, m) for (o, m) in obj_meth
                  if o not in _REG_OBJS and not any(v in m for v in reg_vocab)}
    # registry REMOVE signal: a registry call whose last bool arg is `true` (removePosition=true)
    remove = has_reg and bool(_REMOVE_FLAG.search(body))
    guard = any(g in blow for g in _t("emptiness_guard_vocab", []))
    return {
        "name": name, "visibility": (visibility or "").lower(), "mutability": (mutability or "").lower(),
        "obj_meth": obj_meth, "reg_calls": reg_calls, "has_reg": has_reg,
        "subject_calls": subj_calls, "is_remove": remove, "has_emptiness_guard": guard,
    }


def _external(f) -> bool:
    return f["visibility"] in ("external", "public", "")


def _mutating(f) -> bool:
    return f["mutability"] not in ("view", "pure")


def classify_contract(feats: list, contract: str = "") -> list:
    """Contract-level: feats = list of extract_registry_features dicts for one contract."""
    cands = []
    updaters = [f for f in feats if f["has_reg"] and _mutating(f)]
    if not updaters:
        return []

    # ---- Shape 1: missing_registry_update (H-23) ----
    # subject-proxy objects that registry-updaters mutate via a position method
    subject_objs = set()
    for u in updaters:
        for (o, m) in u["subject_calls"]:
            subject_objs.add(o)
    for f in feats:
        if f["has_reg"] or not _external(f) or not _mutating(f):
            continue
        generic = set(_t("generic_collection_methods", []))
        for (o, m) in f["subject_calls"]:
            # the subject method must be a SPECIFIC protocol op, not a bare collection op
            # (EnumerableSet .add/.remove/.pop are internal storage mutations, not position calls)
            if m in generic:
                continue
            if o in subject_objs and _has_lifecycle_verb(m) and not _is_amount_only(m):
                # an updater must actually mutate the SAME proxy object (shared subject)
                sib = next((u["name"] for u in updaters if any(oo == o for (oo, mm) in u["subject_calls"])), None)
                if not sib:
                    continue
                cands.append({
                    "shape": "missing_registry_update", "parity_type": "registry_parity",
                    "confidence": "high", "function": f["name"], "missing_component": "registry update",
                    "subject": f"{o}.{m}", "sibling_updater": sib,
                    "evidence": f"{contract}.{f['name']} mutates the position subject `{o}.{m}` (lifecycle) "
                                f"like its registry-updating sibling {sib}, but omits the registry update "
                                f"({sib} calls a registry mutator; {f['name']} does not)",
                    "signals": {"subject_obj": o, "sibling": sib},
                })
                break

    # ---- Shape 2: unguarded_registry_remove (H-18) ----
    remove_verbs = _t("remove_verbs", [])
    removers = [f for f in feats if f["is_remove"] and _mutating(f)]
    guarded = [f for f in removers if f["has_emptiness_guard"]]
    if guarded:  # only meaningful if a sibling remove demonstrates the guard
        for f in removers:
            if f["has_emptiness_guard"] or not _external(f):
                continue
            # the unguarded remover must NAME a remove/close op (excludes open*/create* that also pass true)
            if not any(v in f["name"].lower() for v in remove_verbs):
                continue
            sib = guarded[0]["name"]
            cands.append({
                "shape": "unguarded_registry_remove", "parity_type": "registry_parity",
                "confidence": "medium", "function": f["name"], "missing_component": "emptiness guard",
                "subject": "registry remove", "sibling_updater": sib,
                "evidence": f"{contract}.{f['name']} removes a registry position without the emptiness/"
                            f"balance guard its sibling remove {sib} carries — position may be removed while "
                            f"collateral/stake remains",
                "signals": {"sibling": sib},
            })

    # de-dup by (shape, function)
    seen, uniq = set(), []
    for c in cands:
        k = (c["shape"], c["function"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(c)
    return uniq
