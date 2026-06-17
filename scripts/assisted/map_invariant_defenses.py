#!/usr/bin/env python3
"""
map_invariant_defenses.py — P101 automatic DEFENSE mapping per candidate invariant (RESEARCH-ONLY, UN-WIRED).

For a candidate invariant + the function's source text, scan for defense primitives (require/revert, role/auth
modifiers, cap/limit comparisons, state-update ordering, external/staticcall boundaries, recovery paths, existing
invariant-like asserts) and classify how well each covers the invariant:
  COVERS | PARTIALLY_COVERS | DOES_NOT_COVER | UNKNOWN_NEEDS_TRACE

This is an advisory heuristic text-scan. It never validates, promotes, sets severity, or submits. It is a
PRECISION aid: a defense that COVERS the invariant (with no bypass shown) is grounds to reject the hypothesis —
recall expansion must NOT bypass defenses.

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}

COVERS = "COVERS"
PARTIALLY_COVERS = "PARTIALLY_COVERS"
DOES_NOT_COVER = "DOES_NOT_COVER"
UNKNOWN_NEEDS_TRACE = "UNKNOWN_NEEDS_TRACE"

# defense primitive detectors: name -> regex over (lowercased) source text.
_PRIMS = {
    "require_revert": re.compile(r"\brequire\s*\(|\brevert"),
    "role_auth_modifier": re.compile(r"only[a-z]+\b|require\(msg\.sender\s*==|_checkrole|hasrole|onlyrole"),
    "buyer_seller_guard": re.compile(r"msg\.sender\s*!=\s*[\w.]*seller|[\w.]*seller\s*!=\s*msg\.sender|buyer\s*!=\s*seller"),
    "cap_limit_check": re.compile(r"<=\s*\w*(limit|cap|max)|require\([^)]*(limit|cap|max)|>\s*\w*(limit|cap|max)"),
    "nonreentrant": re.compile(r"nonreentrant|reentrancyguard"),
    "state_update_after_checks": re.compile(r"(status|balance|sold|bought|claimed)\s*[-+]?=|_writestate|_writ"),
    "external_boundary": re.compile(r"staticcall|\.call\(|external\s|interface\s|hooks\.|oracle"),
    "recovery_path": re.compile(r"withdraw|claim|redeem|release|rescue|unlock"),
    "existing_invariant_assert": re.compile(r"invariant|assert\(|conservation|sum\s*<=|<=\s*total"),
}

# which primitives are relevant to which invariant category (drives COVERS vs DOES_NOT_COVER).
_RELEVANT = {
    "role_access": ["role_auth_modifier", "buyer_seller_guard", "require_revert"],
    "cap_limit": ["cap_limit_check", "require_revert"],
    "value_conservation": ["existing_invariant_assert", "state_update_after_checks"],
    "per_user_accounting": ["state_update_after_checks", "existing_invariant_assert"],
    "ordering_race": ["nonreentrant", "state_update_after_checks", "require_revert"],
    "lifecycle_state_transition": ["require_revert", "state_update_after_checks"],
    "index_array_integrity": ["role_auth_modifier", "require_revert"],
    "reward_fee_distribution": ["state_update_after_checks", "existing_invariant_assert"],
    "cross_contract_consistency": ["external_boundary"],
    "recovery_availability": ["recovery_path", "require_revert"],
    "negative_space_missing_update": ["state_update_after_checks"],
}


def _detect(text: str) -> Dict[str, bool]:
    t = text.lower()
    return {name: bool(rx.search(t)) for name, rx in _PRIMS.items()}


def map_defenses(invariant: Optional[Dict[str, Any]] = None, source_text: str = "") -> Dict[str, Any]:
    """Classify defenses for one invariant against the function source. Pure; advisory only."""
    inv = invariant or {}
    cat = str(inv.get("invariant_type") or "")
    text = source_text or inv.get("source_snippet") or ""
    present = _detect(text)
    relevant = _RELEVANT.get(cat, [])

    defenses: List[Dict[str, Any]] = []
    for prim in relevant:
        if not text.strip():
            cls = UNKNOWN_NEEDS_TRACE
        elif present.get(prim):
            cls = COVERS
        else:
            cls = DOES_NOT_COVER
        defenses.append({"defense": prim, "classification": cls,
                         "evidence": "primitive present in source" if present.get(prim)
                         else ("no source supplied" if not text.strip() else "primitive absent from supplied source")})

    # aggregate coverage for the invariant:
    classes = [d["classification"] for d in defenses]
    if not text.strip() or not defenses:
        coverage = UNKNOWN_NEEDS_TRACE
    elif COVERS in classes and all(c in (COVERS,) for c in classes):
        coverage = COVERS
    elif COVERS in classes:
        coverage = PARTIALLY_COVERS
    else:
        coverage = DOES_NOT_COVER

    # a single explicit guard that directly addresses the break can fully COVER (e.g. buyer!=seller for role_access)
    if cat == "role_access" and present.get("buyer_seller_guard"):
        coverage = COVERS
    if cat == "cross_contract_consistency" and present.get("external_boundary"):
        coverage = UNKNOWN_NEEDS_TRACE  # boundary exists but the value across it must be traced

    return {
        **FLAGS,
        "invariant_type": cat,
        "coverage": coverage,
        "defenses": defenses,
        "advisory": "Defense mapping is advisory. COVERS (no bypass shown) is grounds to REJECT the hypothesis; "
                    "PARTIALLY_COVERS / DOES_NOT_COVER / UNKNOWN_NEEDS_TRACE proceed to source trace.",
    }


def _self_test() -> int:
    ok = True
    def chk(cond, m):
        nonlocal ok; ok &= bool(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {m}")

    # role_access WITH a buyer!=seller guard -> COVERS
    cov = map_defenses({"invariant_type": "role_access"},
                       'require(msg.sender != listing.seller, "no self purchase"); require(msg.sender==s2Admin)')
    chk(cov["coverage"] == COVERS, "role_access with buyer!=seller guard -> COVERS")

    # role_access WITHOUT the guard -> DOES_NOT_COVER (only referral check present)
    nocov = map_defenses({"invariant_type": "role_access"}, 'require(msg.sender != _referral)')
    chk(nocov["coverage"] in (DOES_NOT_COVER, PARTIALLY_COVERS), "role_access w/o buyer!=seller -> not COVERS")

    # cap_limit with a require(<= cap) but inflatable basis -> at least PARTIAL (require present)
    cap = map_defenses({"invariant_type": "cap_limit"}, "require(sold <= sellLimit)")
    chk(cap["coverage"] in (COVERS, PARTIALLY_COVERS), "cap_limit with require(<=limit) -> covers/partial")

    # per_user_accounting with no asserts -> DOES_NOT_COVER (partial-coverage detection)
    pua = map_defenses({"invariant_type": "per_user_accounting"}, "bought += amount;")
    chk(pua["coverage"] in (PARTIALLY_COVERS, DOES_NOT_COVER), "per_user_accounting partial/none detected")

    # cross_contract -> boundary exists -> UNKNOWN_NEEDS_TRACE (must read across)
    cc = map_defenses({"invariant_type": "cross_contract_consistency"}, "pool.staticcall(...)")
    chk(cc["coverage"] == UNKNOWN_NEEDS_TRACE, "cross_contract boundary -> UNKNOWN_NEEDS_TRACE")

    # no source -> UNKNOWN_NEEDS_TRACE
    ns = map_defenses({"invariant_type": "ordering_race"}, "")
    chk(ns["coverage"] == UNKNOWN_NEEDS_TRACE, "no source -> UNKNOWN_NEEDS_TRACE")

    chk(FLAGS["is_gate"] is False, "FLAGS un-wired")
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--invariant", help="invariant JSON")
    ap.add_argument("--source", help="path to source file (text scanned)")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    inv = json.loads(Path(args.invariant).read_text()) if args.invariant else {}
    src = Path(args.source).read_text() if args.source else ""
    print(json.dumps(map_defenses(inv, src), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
