#!/usr/bin/env python3
"""
comparand_parity_gate.py — Phase-34 RESEARCH-ONLY precision gate for sibling-call mechanisms (un-wired).

P33 showed the P32 discriminator's missing_call / recipient_missing rule advances STRONG on merely ≥1 shared call +
any missing call, which under AUTONOMOUS enumeration produced confident false positives (it regressed the P32 BakerFi
negative control and over-advanced on dittoeth). This gate is a POST-FILTER applied ONLY to advanced
missing_call / recipient_missing mechanisms: it requires a REAL parity relationship before such a mechanism may keep
advancing. The P32 discriminator (3ce7dae0) is NOT modified; this is a separate module the P34 wrapper invokes.

The parity bar is REUSED verbatim from the validated sibling-parity platform
(sibling_function_parity_taxonomy.classify_pair + config/sibling_function_parity_patterns.json): a candidate survives
ONLY if classify_pair, run on (comparand-sibling = strong, target = weak), emits a candidate whose `weak` is the
target and whose `missing_component` matches the omitted call. That bar already encodes:
  - two-signal kinship (name-stem/core OR >=2 shared calls & jaccard>=0.3),
  - a shared MUTATING path,
  - a controlled-vocabulary component (validation/recipient/cap/access/registry/pause), NOT a getter/cast/event,
  - wrapper / both-admin / external-reachability / exclude_components suppression.
This is principled reuse, not subject special-casing: it independently rejects the P33 noise (no kinship + omitted
calls outside the component vocab) while passing the genuine Blackhole recipient parity (claim/claim_many +
getOriginalOwner).

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: comparand_parity_gate.py --self-test
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # classify_pair + helpers + config  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}
# All mechanisms whose STRONG confidence derives from a "sibling has a call the target lacks" comparand delta —
# the over-permissive shape P33 exposed. missing_call/recipient_missing carry the omitted call in `term`; wrong_basis
# (_rule_basis) advances STRONG on a sibling conversion call (convert/normalize/tovalue) the target omits, with no
# `term`, so the gate derives that conversion call. (A1's wrong_basis is WEAK and A2 has none, so this is harmless to
# the positive anchors — it closes the same structural gap, not a subject-specific case.)
_SIBLING_MECHANISMS = {"missing_call", "recipient_missing", "wrong_basis"}
_CONVERSION_TOKENS = ("convert", "normalize", "tovalue")  # mirrors _rule_basis in root_cause_discriminator


def _feat(fn: dict):
    return sfp.extract_features(fn.get("name", ""), fn.get("signature", ""), fn.get("modifiers", []),
                               fn.get("snippet", ""), fn.get("visibility", ""))


def _match(omitted: str, component: str) -> bool:
    a, b = (omitted or "").lower(), (component or "").lower()
    return bool(a) and bool(b) and (a in b or b in a)


def gate(target: dict, siblings: list, omitted_call: str, mechanism: str) -> dict:
    """parity_pass + structured reasons for a single missing_call/recipient_missing candidate."""
    out = {**FLAGS, "mechanism": mechanism, "omitted_call": omitted_call, "parity_pass": False,
           "stem_kinship": False, "shared_operation_family": "unknown", "shared_mutating_state": False,
           "shared_value_domain": False, "omitted_call_effect": None, "comparand": None,
           "matched_component": None, "confidence": None, "rejection_reason": None}
    tf = _feat(target)

    # comparand siblings = those whose body actually contains the omitted call
    comparands = [s for s in siblings if omitted_call.lower() in {c.lower() for c in _feat(s)["calls"]}]
    if not comparands:
        out["rejection_reason"] = f"omitted call '{omitted_call}' is not present in any sibling body — no comparand"
        return out

    best_diag = None
    for s in comparands:
        sf = _feat(s)
        is_sib, name_kin, jacc, shared = sfp._siblings(sf, tf)
        shared_mut = sfp._shared_mutating(sf, tf)
        comp_type = sfp._component_type(omitted_call)
        # record best-effort diagnostics from the strongest comparand attempt
        diag = {"comparand": sf["name"], "name_kin": name_kin, "shared_mut": shared_mut, "comp_type": comp_type,
                "is_sib": is_sib, "weak_reachable": tf["visibility"] in ("external", "public", "")}
        best_diag = diag if best_diag is None else best_diag

        for c in sfp.classify_pair(sf, tf):  # strong-candidate = sibling, weak = target
            if c["weak"] == tf["name"] and _match(omitted_call, c["missing_component"]):
                out.update({"parity_pass": True, "stem_kinship": bool(c["signals"]["name_kin"]),
                            "shared_operation_family": "name_kin" if c["signals"]["name_kin"] else "behavioral",
                            "shared_mutating_state": shared_mut, "shared_value_domain": bool(sf["writes"] & tf["writes"]),
                            "omitted_call_effect": c["parity_type"], "comparand": sf["name"],
                            "matched_component": c["missing_component"], "confidence": c["confidence"],
                            "rejection_reason": None})
                return out

    # parity FAILED — attribute the strongest reason from the best comparand attempt
    d = best_diag
    out.update({"stem_kinship": d["name_kin"], "shared_mutating_state": d["shared_mut"],
                "omitted_call_effect": d["comp_type"], "comparand": d["comparand"]})
    if not d["is_sib"]:
        reason = "no sibling kinship (no stem/core match and <2 shared calls / low jaccard)"
    elif not d["weak_reachable"]:
        reason = f"target '{tf['name']}' is internal/private — not externally reachable (by-design omission)"
    elif not d["shared_mut"]:
        reason = "no shared mutating path between target and comparand"
    elif not d["comp_type"]:
        reason = f"omitted call '{omitted_call}' is not a controlled parity component (getter/decorative/uncontrolled)"
    else:
        reason = "no controlled-vocabulary component asymmetry on a shared mutating path"
    out["rejection_reason"] = reason
    return out


def _conversion_call(target: dict, siblings: list) -> str:
    """The conversion call (convert/normalize/tovalue) a sibling has and the target lacks — the comparand that drives
    a STRONG wrong_basis. Returns '' if none (then wrong_basis is not a sibling-delta and passes through)."""
    tcalls = {c.lower() for c in _feat(target)["calls"]}
    for s in siblings:
        for c in {c.lower() for c in _feat(s)["calls"]} - tcalls:
            if any(tok in c for tok in _CONVERSION_TOKENS):
                return c
    return ""


def filter_advanced(target: dict, siblings: list, advanced: list) -> tuple[list, list, list]:
    """Apply the gate to advanced sibling-comparand-delta mechanisms (missing_call/recipient_missing/wrong_basis).
    Returns (survivors, demoted, gate_reports). Non-sibling-delta mechanisms pass through untouched."""
    survivors, demoted, reports = [], [], []
    for m in advanced:
        if m["mechanism"] not in _SIBLING_MECHANISMS:
            survivors.append(m)
            continue
        omitted = m.get("term", "") or (_conversion_call(target, siblings) if m["mechanism"] == "wrong_basis" else "")
        if m["mechanism"] == "wrong_basis" and not omitted:
            survivors.append(m)  # not driven by a sibling-conversion delta — leave untouched
            continue
        g = gate(target, siblings, omitted, m["mechanism"])
        reports.append({"label": m.get("label"), **{k: g[k] for k in
                        ("parity_pass", "stem_kinship", "shared_operation_family", "shared_mutating_state",
                         "shared_value_domain", "omitted_call_effect", "comparand", "matched_component",
                         "confidence", "rejection_reason")}})
        if g["parity_pass"]:
            survivors.append(m)
        else:
            demoted.append({"label": m.get("label"), "confidence": "REJECT",
                            "reason": f"comparand_parity_gate: {g['rejection_reason']}"})
    return survivors, demoted, reports


# --------------------------------- self-test ---------------------------------

def _self_test():
    ok = True
    # PROBE 1 — Blackhole-shaped PASS: claim/claim_many (stem kin) + getOriginalOwner (recipient component) on a
    # shared mutating (transfer) path, weak is public -> parity_pass.
    target = {"name": "claim_many", "visibility": "external",
              "snippet": "for (uint i; i<ids.length; i++){ address o = escrow.ownerOf(ids[i]); token.transfer(o, amt[i]); }"}
    sib = {"name": "claim", "visibility": "external",
           "snippet": "address o = escrow.ownerOf(id); o = avm.getOriginalOwner(id); token.transfer(o, amt);"}
    g1 = gate(target, [sib], "getOriginalOwner", "recipient_missing")
    print(f"  [{'PASS' if g1['parity_pass'] else 'FAIL'}] Blackhole recipient parity PASSES "
          f"(component={g1['matched_component']}, stem_kin={g1['stem_kinship']})")
    ok &= g1["parity_pass"]
    # PROBE 2 — decorative-getter REJECT: same stem-kin pair but the omitted call is a config getter (not a
    # controlled component) -> reject on component vocab.
    sib2 = {"name": "claim", "visibility": "external",
            "snippet": "uint m = settings().getMaxAge(); address o = escrow.ownerOf(id); token.transfer(o, amt);"}
    g2 = gate(target, [sib2], "getMaxAge", "missing_call")
    print(f"  [{'PASS' if not g2['parity_pass'] else 'FAIL'}] decorative getter REJECTED ({g2['rejection_reason']})")
    ok &= not g2["parity_pass"]
    # PROBE 3 — no-kinship REJECT: unrelated names, no stem/core, omitted call outside vocab.
    tgt3 = {"name": "_getPosition", "visibility": "internal",
            "snippet": "(uint c, uint d) = _getMMPosition(); p = oracle.getSafeLatestPrice(age).price;"}
    sib3 = {"name": "_toWETH", "visibility": "internal",
            "snippet": "o = (a * c.getSafeLatestPrice(settings().getPriceMaxAge()).price) / d;"}
    g3 = gate(tgt3, [sib3], "getPriceMaxAge", "missing_call")
    print(f"  [{'PASS' if not g3['parity_pass'] else 'FAIL'}] no-kinship/decorative REJECTED ({g3['rejection_reason']})")
    ok &= not g3["parity_pass"]
    # PROBE 4 — non-comparand: omitted call appears in NO sibling -> reject.
    g4 = gate(target, [sib], "nonexistentCall", "missing_call")
    print(f"  [{'PASS' if not g4['parity_pass'] else 'FAIL'}] missing-from-all-siblings REJECTED ({g4['rejection_reason']})")
    ok &= not g4["parity_pass"]
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (gate is a library used by the P34 wrapper)")


if __name__ == "__main__":
    raise SystemExit(main())
