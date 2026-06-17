#!/usr/bin/env python3
"""
admin_capability_parity_taxonomy.py — pure (no-I/O) helpers + classifier for the ADMIN CAPABILITY-PARITY lens.

Generalized CLASS of the P304 centrifuge M-06 miss: an admin/role/Auth contract exposes one half of a known
capability PAIR (add/remove, pause/unpause, grant/revoke, schedule/cancel, freeze/unfreeze, enable/disable,
rely/deny, lock/unlock, register/deregister) but NOT the inverse -> a granted capability cannot be reversed.

Two-signal:  S1 the contract is an admin/role/Auth contract  AND  S2 a capability-pair half present (external/public)
while its inverse is absent.  A prefix matches only at a camelCase boundary (addPauser, not 'additional').

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes. High precision over
recall. The per-contract function-name set + admin-marker correlation is done by the audit runner; this module is
pure. Anchored on centrifuge admins/PauseAdmin.sol (pause without unpause).

HONEST SCOPE: generalizes the admin capability-asymmetry class / recalls the M-06 subsystem; the exact
cross-contract DelayedAdmin<->PauseAdmin role-graph gap is beyond a static lens.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "admin_capability_parity_patterns.json"


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key: str, default):
    return _cfg().get(key, default)


def is_admin_contract(contract: str, blob: str) -> bool:
    clow = (contract or "").lower()
    if any(t in clow for t in _t("admin_name_terms", [])):
        return True
    b = (blob or "").lower()
    return any(m in b for m in _t("admin_markers", []))


def _matches_prefix(name: str, pfx: str) -> str | None:
    """If `name` begins with `pfx` at a camelCase boundary, return the suffix; else None. name/pfx are RAW case."""
    nl, pl = name.lower(), pfx.lower()
    if nl == pl:
        return ""
    if nl.startswith(pl) and len(name) > len(pfx):
        nxt = name[len(pfx)]
        if nxt.isupper() or not nxt.isalpha():
            return name[len(pfx):]
    return None


def classify_contract(contract: str, fn_names: list, blob: str) -> list:
    """fn_names = external/public function names (RAW case). Returns deduped missing-inverse candidates. Pure."""
    if not is_admin_contract(contract, blob):
        return []
    names = list(fn_names)
    lower = {n.lower() for n in names}
    role_restricted = {tuple(p) for p in _t("role_restricted_pairs", [])}
    role_terms = _t("role_suffix_terms", [])
    out, seen_missing = [], set()
    for pfx, inv in _t("capability_pairs", []):
        for n in names:
            suffix = _matches_prefix(n, pfx)
            if suffix is None:
                continue
            # add/remove & register/deregister fire only on role/permission suffixes (skip append-only registries)
            if (pfx, inv) in role_restricted and not any(t in suffix.lower() for t in role_terms):
                continue
            inverse = (inv + suffix).lower()
            if inverse in lower:
                continue                      # symmetric -> not a gap
            missing = inv + suffix
            if missing.lower() in seen_missing:
                continue
            seen_missing.add(missing.lower())
            out.append({
                "finding_shape": "admin_capability_parity",
                "confidence": "medium",
                "present_capability": n,
                "missing_inverse": missing,
                "explanation": (f"{contract} (admin/role contract) exposes `{n}` but not its inverse `{missing}` — "
                                f"a granted/applied capability cannot be reversed by this contract, so the action "
                                f"taken via `{n}` has no counterpart to undo it (centrifuge M-06 class)."),
                "signals": {"S1_admin_contract": True, "S2_present_without_inverse": [n, missing]},
                "suppression_status": "none",
            })
    return out
