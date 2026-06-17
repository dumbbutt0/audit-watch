#!/usr/bin/env python3
"""
eip712_domain_separator_staleness_taxonomy.py — pure (no-I/O) helpers + classifier for the EIP-712 DOMAIN_SEPARATOR
STALENESS research lens.

Generalized CLASS of the P304 centrifuge M-03 miss: a contract caches an EIP-712 DOMAIN_SEPARATOR at construction
from `name`/`version`, but `name`/`version` is mutable post-construction (a setter / `file('name')`, or never set in
the ctor). The cached separator then does not match the live name -> EIP-712/permit signatures fail.

Two-signal AND:  S1 a domain separator cached in the constructor from name/version  AND  S2 name/version mutable
post-construction.  Suppressions: name+version fixed in the ctor with no setter; pure libs.

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes. High precision over
recall. The cross-function correlation (ctor body + setters) is performed by the audit runner; this module is pure.
Anchored on centrifuge token/ERC20.sol.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "eip712_domain_separator_staleness_patterns.json"
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key: str, default):
    return _cfg().get(key, default)


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _any(text: str, terms) -> bool:
    return any(w in text for w in terms)


def references_domain_sep(body: str) -> bool:
    """True iff the body assigns/computes a cached domain separator (var assignment or a domain-calc call)."""
    b = strip_comments(body or "").lower()
    if any(v in b and (v + " =" in b or v + "=" in b or v + " :=" in b) for v in _t("domain_sep_vars", [])):
        return True
    return _any(b, _t("domain_calc_calls", []))


def name_assigned(body: str) -> bool:
    b = strip_comments(body or "").lower()
    return _any(b, _t("name_set_in_ctor_terms", []))


def classify_contract(contract: str, ctor_body: str, calc_blob: str, mutator_blob: str,
                      kind_is_library: bool = False) -> list:
    """Return 0..1 candidate. ctor_body = the constructor body; calc_blob = ctor + any *domain* helper bodies (for
    the name/version reference); mutator_blob = all NON-ctor function bodies (for a post-ctor name mutator). Pure."""
    clow = (contract or "").lower()
    if kind_is_library or any(clow == n or clow.endswith(n) for n in _t("suppress_library_contracts", [])):
        return []

    ctor = strip_comments(ctor_body or "").lower()
    calc = strip_comments(calc_blob or "").lower()
    mut = strip_comments(mutator_blob or "").lower()

    # ---- S1: a domain separator cached in the ctor, computed from name/version ----
    cached_in_ctor = references_domain_sep(ctor)
    sep_uses_name = _any(calc, _t("name_version_terms", []))
    if not (cached_in_ctor and sep_uses_name):
        return []

    # ---- S2: name/version mutable post-construction ----
    name_in_ctor = name_assigned(ctor)
    mutator_present = _any(mut, _t("name_mutator_terms", []))
    if not (mutator_present or not name_in_ctor):
        return []   # name fixed in ctor, no setter -> not stale

    confidence = "high" if (mutator_present and not name_in_ctor) else "medium"
    why = ("name set post-ctor via a setter/file() and never in the ctor" if (mutator_present and not name_in_ctor)
           else "a post-ctor name/version mutator exists" if mutator_present
           else "name/version never assigned in the constructor")
    return [{
        "finding_shape": "eip712_domain_separator_staleness",
        "confidence": confidence,
        "explanation": (f"{contract} caches an EIP-712 DOMAIN_SEPARATOR in the constructor computed from "
                        f"name/version, but {why} — the cached separator does not match the live name, so "
                        f"permit/EIP-712 signatures verify against the wrong domain (centrifuge M-03 class)."),
        "signals": {"S1_cached_separator_from_name": True, "S2_name_mutable": True,
                    "name_in_ctor": name_in_ctor, "post_ctor_mutator": mutator_present},
        "suppression_status": "none",
    }]
