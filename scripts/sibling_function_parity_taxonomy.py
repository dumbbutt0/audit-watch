#!/usr/bin/env python3
"""
sibling_function_parity_taxonomy.py — pure (no-I/O) classifier for the SIBLING-FUNCTION PARITY research
lens. Anchored on Blackhole M-04 (RewardsDistributor.claim resolves avm.getOriginalOwner inside an AVM
guard; claim_many omits the whole block → AVM-managed-lock rewards sent to the wrong recipient).

Two public pure functions:
  extract_features(name, signature, modifiers, snippet) -> dict   (per-function feature set)
  classify_pair(fa, fb) -> list                                   (0+ parity candidates for the pair)

RESEARCH-ONLY: the audit that uses this is read-only, is_gate:false, routes_in_production:false — never
mints or routes. High precision over recall (false negatives accepted; high-confidence FPs not).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "sibling_function_parity_patterns.json"

_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
_CALL = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")
_DOTCALL = re.compile(r"\.([A-Za-z_]\w*)\s*\(")
_REQUIRE = re.compile(r"\brequire\s*\(|\brevert\b|\bif\s*\([^)]*\)\s*(?:revert|return|break)")
_WRITE = re.compile(r"([A-Za-z_]\w*(?:\[[^\]]*\])?(?:\.[A-Za-z_]\w*)?)\s*(?:\+=|-=|=)(?![=])")
_EMIT = re.compile(r"\bemit\s+([A-Za-z_]\w*)")
_MSGSENDER = re.compile(r"msg\.sender")
_KEYWORDS = {"if", "for", "while", "return", "require", "revert", "assert", "emit", "memory", "storage",
             "uint", "uint256", "int", "address", "bool", "bytes", "bytes32", "new", "else", "break",
             "continue", "function", "mapping", "struct", "type", "abi"}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key, default):
    return _cfg().get(key, default)


def strip_comments(code: str) -> str:
    return _COMMENT.sub(" ", code or "")


def _stem(name: str) -> str:
    s = (name or "").lower().lstrip("_")
    for a in sorted(_t("variant_affixes", []), key=len, reverse=True):
        if s.endswith(a) and len(s) > len(a) + 2:
            return s[: -len(a)]
    return s


def _core(name: str) -> str:
    """Stem after also stripping a leading paired-action verb (validateX/executeX -> x). Lets
    validate*/execute*/simulate* siblings (shared suffix, different verb) be recognized as kin."""
    s = _stem(name)
    for v in sorted(_t("sibling_prefix_verbs", []), key=len, reverse=True):
        if v and s.startswith(v) and len(s) > len(v) + 3:
            return s[len(v):]
    return s


def _is_excluded(token: str) -> bool:
    """Drop events / interface casts / type constructors / pure getters — these dominate corpus noise.
    Real validator/resolution calls are lowerCamel; events & casts start uppercase."""
    if not token:
        return True
    if token[0].isupper():            # events (Transfer), interface casts (IERC20), structs
        return True
    if token.lower() in set(_t("exclude_components", [])):
        return True
    return False


def extract_features(name: str, signature: str = "", modifiers=None, snippet: str = "",
                     visibility: str = "") -> dict:
    """Pure per-function feature extraction. snippet = brace-matched body (may include +1 helper)."""
    body = strip_comments(snippet or "")
    calls = {c for c in _CALL.findall(body) if c not in _KEYWORDS}
    calls |= set(_DOTCALL.findall(body))
    writes = {w for w in _WRITE.findall(body) if w not in _KEYWORDS and not w.isdigit()}
    return {
        "name": name or "",
        "stem": _stem(name or ""),
        "core": _core(name or ""),
        "visibility": (visibility or "").lower(),
        "modifiers": [m.lower() for m in (modifiers or [])],
        "calls": calls,
        "writes": writes,
        "emits": set(_EMIT.findall(body)),
        "require_count": len(_REQUIRE.findall(body)),
        "msg_sender": bool(_MSGSENDER.search(body)),
        "_ncalls": len(calls),
    }


def _siblings(fa: dict, fb: dict) -> tuple[bool, bool, float, set]:
    """Return (is_sibling, name_kin, jaccard, shared_calls)."""
    shared = fa["calls"] & fb["calls"]
    union = fa["calls"] | fb["calls"]
    jacc = len(shared) / max(1, len(union))
    name_kin = (fa["name"] != fb["name"]
                and ((fa["stem"] == fb["stem"] and bool(fa["stem"]))
                     or (fa["core"] == fb["core"] and bool(fa["core"]) and len(fa["core"]) >= 4)))
    behav = len(shared) >= _t("sibling_min_shared_calls", 2) and jacc >= _t("sibling_min_jaccard", 0.3)
    return (name_kin or behav), name_kin, jacc, shared


def _is_wrapper(this: dict, other: dict) -> bool:
    """this is a thin forwarder/overload of other: its OWN body (pre helper-resolution) directly calls
    the sibling and is tiny. Uses own_calls so +1 helper resolution can't mask the forwarder."""
    own = this.get("own_calls", this["calls"])
    own_n = this.get("own_ncalls", this["_ncalls"])
    return other["name"] in own and own_n <= 3


def _component_type(token: str) -> str | None:
    comps = _t("components", {})
    tl = token.lower()
    for ptype, vocab in comps.items():
        for v in vocab:
            if v in tl:
                return ptype
    return None


def _shared_mutating(fa: dict, fb: dict) -> bool:
    sig = set(_t("mutating_call_signals", []))
    shared = {c.lower() for c in (fa["calls"] & fb["calls"])}
    if any(any(s in c for s in sig) for c in shared):
        return True
    return bool(fa["writes"] & fb["writes"])


def classify_pair(fa: dict, fb: dict) -> list:
    """Return 0+ parity candidates. Each candidate names the weaker sibling (the one missing the
    controlled component). fa/fb are extract_features() dicts."""
    is_sib, name_kin, jacc, shared = _siblings(fa, fb)
    if not is_sib:
        return []
    # wrapper / overload suppression (either direction)
    if _is_wrapper(fa, fb) or _is_wrapper(fb, fa):
        return []
    # both-admin suppression
    admin = set(_t("admin_modifiers", []))
    both_admin = bool(set(fa["modifiers"]) & admin) and bool(set(fb["modifiers"]) & admin)
    if both_admin:
        return []
    if not _shared_mutating(fa, fb):
        return []

    cands = []
    # direction helper: STRONG has the component, WEAK is missing it
    def emit_dir(strong, weak):
        # reachability gate: the WEAK sibling must be externally reachable. The classic
        # fn(external, guarded) / _fn(internal, unguarded) pair is correct-by-design (the internal impl
        # is only reached through the guarded public) — suppress when weak is internal/private.
        if weak["visibility"] not in ("external", "public", ""):
            return
        only = {c for c in (strong["calls"] - weak["calls"]) if not _is_excluded(c) and c != weak["name"]}
        seen = set()
        for tok in sorted(only):
            ptype = _component_type(tok)
            if not ptype or ptype in seen:
                continue
            seen.add(ptype)
            # name-stem siblings are the high-precision tier (corpus-validated). Behavioral-kinship
            # pairs (shared calls, different name) are noisier cross-products → demote to low.
            conf = ("high" if (name_kin and len(shared) >= 2) else "medium" if name_kin else "low")
            cands.append({
                "parity_type": ptype, "missing_component": tok,
                "strong": strong["name"], "weak": weak["name"], "confidence": conf,
                "evidence": f"{strong['name']} calls {tok} ({ptype}); {weak['name']} omits it on a shared mutating path",
                "signals": {"name_kin": name_kin, "shared_calls": sorted(shared)[:8], "jaccard": round(jacc, 2)},
            })
        # require-count asymmetry (validation_parity) — weak/context-only heuristic: a raw guard-count
        # delta is noisy (helper-relocated guards, loop scaffolding), so it is LOW confidence and only
        # emitted for name-stem siblings. High/medium are reserved for a specific missing controlled call.
        if (name_kin and strong["require_count"] - weak["require_count"] >= 2
                and "validation_parity" not in seen):
            seen.add("validation_parity")
            cands.append({
                "parity_type": "validation_parity",
                "missing_component": f"require/guard x{strong['require_count'] - weak['require_count']}",
                "strong": strong["name"], "weak": weak["name"], "confidence": "low",
                "evidence": f"{strong['name']} has {strong['require_count']} guards vs {weak['name']} "
                            f"{weak['require_count']} on a shared mutating path",
                "signals": {"name_kin": name_kin, "shared_calls": sorted(shared)[:8], "jaccard": round(jacc, 2)},
            })
        # modifier asymmetry (access_control_parity) — strong gated, weak not, weak not internal-only
        sm, wm = set(strong["modifiers"]), set(weak["modifiers"])
        gated = (sm & admin) - wm
        if gated and not (wm & admin) and "access_control_parity" not in seen:
            seen.add("access_control_parity")
            cands.append({
                "parity_type": "access_control_parity",
                "missing_component": f"modifier:{sorted(gated)[0]}",
                "strong": strong["name"], "weak": weak["name"],
                "confidence": "high" if (name_kin and len(shared) >= 2) else "medium" if name_kin else "low",
                "evidence": f"{strong['name']} is {sorted(gated)[0]}; {weak['name']} lacks an equivalent gate",
                "signals": {"name_kin": name_kin, "shared_calls": sorted(shared)[:8], "jaccard": round(jacc, 2)},
            })

    emit_dir(fa, fb)
    emit_dir(fb, fa)
    # de-dup by (parity_type, weak, missing_component)
    seen, uniq = set(), []
    for c in cands:
        k = (c["parity_type"], c["weak"], c["missing_component"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(c)
    return uniq


if __name__ == "__main__":  # tiny smoke
    import sys
    a = extract_features("claim", snippet="x=_claim(); if(avm)getOriginalOwner(t); token.transfer(o,a);")
    b = extract_features("claim_many", snippet="for(;;){x=_claim(); token.transfer(o,a);}")
    print(json.dumps(classify_pair(a, b), indent=2))
