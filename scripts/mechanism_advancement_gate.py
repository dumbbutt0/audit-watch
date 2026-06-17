#!/usr/bin/env python3
"""
mechanism_advancement_gate.py — Phase-45 RESEARCH-ONLY generalized advancement gate (un-wired).

Runs AFTER mechanism discrimination, on candidates whose pre-gate state is ADVANCE, and TIGHTENS (only ever demotes:
ADVANCE -> REVIEW_ONLY/ABSTAIN; never promotes). Applies P34-calibre corroboration to EVERY mechanism family — the
previously-ungated missing_bound/missing_cap/omitted_term/missing_scale/computed_unapplied as well as the sibling-call-
delta families (which still route through the UNCHANGED comparand_parity_gate / P34; this gate only adds checks).

Five global checks: operation_kinship · shared_value_domain · downstream_effect · non_design_absence ·
source_corroboration. A candidate ADVANCEs only if all REQUIRED checks (per mechanism) pass; non_design_absence fail ->
ABSTAIN; corroboration-only fail -> REVIEW_ONLY. Generic only — no subject identifiers.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: mechanism_advancement_gate.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "mechanism_advancement_gate.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # noqa: E402
import comparand_parity_gate as PG  # P34, reused unchanged  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _body(target) -> str:
    return sfp.strip_comments(target.get("snippet", "") or "")


def _is_interface(target) -> bool:
    c = target.get("contract", "") or ""
    f = (target.get("file", "") or "").lower()
    if re.match(_cfg()["interface_contract_re"], c):
        return True
    return any(s in f for s in _cfg()["interface_file_signals"])


def _is_view_getter(target) -> bool:
    mut = (target.get("mutability", "") or "").lower()
    name = (target.get("name", "") or "").lower()
    return mut in _cfg()["view_mutabilities"] and bool(re.match(r"^_?(" + _cfg()["getter_name_re"][2:], name))


def _non_design_absence(target, mech):
    name = (target.get("name", "") or "").lower()
    if name in _cfg()["standard_token_primitives"]:
        return False, f"standard-token primitive '{name}'"
    if _is_interface(target):
        return False, "interface / declaration-only target"
    if mech in ("missing_bound", "missing_scale") and _is_view_getter(target):
        return False, "view-only getter (bound/scale absence is by-design)"
    return True, None


def _downstream_effect(target, downstream_users):
    if downstream_users:
        return True, list(downstream_users)[:4]
    b = _body(target).lower()
    hits = [s for s in _cfg()["transfer_state_signals"] if s in b]
    return bool(hits), hits[:4]


def _shared_value_domain(target, term, mech):
    c = _cfg()
    t = (term or "").lower()
    if mech == "missing_bound":
        dom = "bound/limit"
    else:
        dom = next((d for d in c["value_authority_domain_terms"] if d in t),
                   "scale/units" if any(s in t for s in c["scale_tokens"]) else "unknown")
    b = _body(target).lower()
    tgt_value = any(d in b for d in c["value_authority_domain_terms"]) or any(s in b for s in c["transfer_state_signals"])
    return (tgt_value and dom != "unknown"), dom


def _kin(target, sib):
    tf = sfp.extract_features(target.get("name", ""), snippet=_body(target))
    sf = sfp.extract_features(sib.get("name", ""), snippet=sfp.strip_comments(sib.get("snippet", "") or ""))
    is_sib, *_ = sfp._siblings(sf, tf)
    return is_sib, sfp._shared_mutating(sf, tf)


def _operation_kinship(target, siblings, mech):
    if mech in _cfg()["intra_function_mechanisms"]:
        return True, "intra-function evidence"
    for s in siblings:
        is_sib, shared_mut = _kin(target, s)
        # operational kinship = name/behavioral sibling OR a shared mutating path (same value operation)
        if is_sib or shared_mut:
            return True, f"kin with {s.get('name')}"
    return False, "no kin/shared-mutating comparand sibling"


def _omitted_computed_corroborated(target, term) -> bool:
    b = _body(target)
    if not term:
        return False
    if not re.search(r"\b" + re.escape(term) + r"\b\s*=(?![=])", b):
        return False  # not computed locally
    for sig in ("safetransfer", "transferfrom", "transfer", "mint", "burn"):
        for m in re.finditer(sig + r"\s*\(([^;]*)\)", b, re.I):
            if term.lower() not in m.group(1).lower():
                return True  # computed but excluded from a value output
    return False


def _bound_or_scale_parity_sibling(target, term, siblings, mech):
    c = _cfg()
    needle = (term or "").lower()
    for s in siblings:
        sb = sfp.strip_comments(s.get("snippet", "") or "").lower()
        if mech == "missing_bound":
            if not (needle and needle in sb) and not any(b in sb for b in c["bound_terms"]):
                continue
        else:  # missing_scale
            if not (any(op in sb for op in c["scale_ops"]) and any(tk in sb for tk in c["scale_tokens"])):
                continue
        is_sib, shared_mut = _kin(target, s)
        # the strong corroborator is a SHARED MUTATING PATH bearing the scale/bound (the P32/P34 signal) — not
        # name/jaccard kinship; different-length siblings legitimately share the key transfer/state op at low jaccard.
        if shared_mut:
            return s.get("name")
    return None


def _source_corroboration(candidate, target, siblings):
    mech = candidate.get("mechanism") or ""
    term = candidate.get("term", "") or ""
    corr = []
    if mech in _cfg()["sibling_call_delta_mechanisms"]:
        omitted = term or (PG._conversion_call(target, siblings) if mech == "wrong_basis" else "")
        g = PG.gate({"name": target.get("name"), "snippet": target.get("snippet", ""), "visibility": target.get("visibility", "")},
                    siblings, omitted, mech)
        if g["parity_pass"]:
            corr.append(f"P34_parity_pass:{g.get('matched_component')}")
    elif mech == "missing_scale":
        sib = _bound_or_scale_parity_sibling(target, term, siblings, "missing_scale")
        if sib:
            corr.append(f"scale_parity_sibling:{sib}")
    elif mech in _cfg()["intra_function_mechanisms"]:
        if _omitted_computed_corroborated(target, term):
            corr.append(f"computed_unapplied_with_effect:{term}")
    elif mech == "missing_bound":
        sib = _bound_or_scale_parity_sibling(target, term, siblings, "missing_bound")
        if sib:
            corr.append(f"bound_parity_sibling:{sib}")
    return (len(corr) > 0), corr


def gate(candidate: dict, target: dict, siblings=None, downstream_users=None) -> dict:
    siblings = siblings or []
    downstream_users = downstream_users or []
    c = _cfg()
    mech = c["_alias"].get(candidate.get("mechanism", ""), candidate.get("mechanism", ""))
    cand = {**candidate, "mechanism": mech}
    reqd = c["required_checks"].get(mech, ["non_design_absence", "source_corroboration"])

    nda_ok, nda_reason = _non_design_absence(target, mech)
    corr_ok, corrs = _source_corroboration(cand, target, siblings)
    kin_ok, kin_reason = _operation_kinship(target, siblings, mech)
    dom_ok, dom = _shared_value_domain(target, cand.get("term", ""), mech)
    dse_ok, uses = _downstream_effect(target, downstream_users)
    checks = {"operation_kinship": {"pass": kin_ok, "reason": kin_reason},
              "shared_value_domain": {"pass": dom_ok, "domain": dom},
              "downstream_effect": {"pass": dse_ok, "uses": uses},
              "non_design_absence": {"pass": nda_ok, "reject_reason": nda_reason},
              "source_corroboration": {"pass": corr_ok, "corroborators": corrs}}

    rej = rev = None
    if all(checks[k]["pass"] for k in reqd):
        decision = "ADVANCE"
    elif not nda_ok:
        decision, rej = "ABSTAIN", nda_reason
    elif not corr_ok:
        decision, rev = "REVIEW_ONLY", "no strong source corroborator (present-elsewhere/absent-here or self-computed alone is insufficient)"
    else:
        decision, rej = "ABSTAIN", "failed required checks: " + ",".join(k for k in reqd if not checks[k]["pass"])
    return {**FLAGS, "candidate_id": candidate.get("label") or candidate.get("candidate_id"), "mechanism_class": mech,
            "target": {"file": target.get("file"), "function": target.get("name"), "lines": target.get("lines")},
            "pre_gate_decision": "ADVANCE", "post_gate_decision": decision, "evidence": checks,
            "rejection_reason": rej, "review_reason": rev}


# --------------------------------- self-test (8 required cases) ---------------------------------

def _t(name, snippet, contract="C", mut="", file="src/C.sol"):
    return {"name": name, "snippet": snippet, "contract": contract, "mutability": mut, "file": file}


def _self_test():
    ok = True
    # 1 standard ERC transfer missing unrelated cap -> ABSTAIN (non-design-absence: primitive)
    r1 = gate({"mechanism": "missing_cap", "term": "cap", "label": "missing_cap"},
              _t("transfer", "balanceOf[to]+=amt; balanceOf[msg.sender]-=amt;", contract="ERC6909"),
              siblings=[_t("setCap", "supplyCap = x;", contract="SuperPool")])
    c1 = r1["post_gate_decision"] == "ABSTAIN" and "primitive" in (r1["rejection_reason"] or "")
    print(f"  [{'PASS' if c1 else 'FAIL'}] ERC transfer missing cap -> ABSTAIN ({r1['rejection_reason']})"); ok &= c1
    # 2 interface getter omitted_term -> ABSTAIN
    r2 = gate({"mechanism": "omitted_term", "term": "feed", "label": "omitted_feed"},
              _t("decimals", "return 8;", contract="IAggregator", file="src/interfaces/IAggregator.sol", mut="view"))
    c2 = r2["post_gate_decision"] == "ABSTAIN"
    print(f"  [{'PASS' if c2 else 'FAIL'}] interface getter omitted_term -> ABSTAIN ({r2['rejection_reason']})"); ok &= c2
    # 3 view-only getter missing_scale -> ABSTAIN
    r3 = gate({"mechanism": "missing_scale", "term": "scale", "label": "missing_scale"},
              _t("getPrice", "return price;", mut="view"), siblings=[_t("convert", "wmul(x, decimals);")])
    c3 = r3["post_gate_decision"] == "ABSTAIN"
    print(f"  [{'PASS' if c3 else 'FAIL'}] view getter missing_scale -> ABSTAIN ({r3['rejection_reason']})"); ok &= c3
    # 4 missing_bound w/ real kinship + shared mutating + downstream -> ADVANCE
    tgt4 = _t("liquidate", "uint take = repay; pool.repay(repay); token.safeTransfer(to, take);", contract="Vault")
    sib4 = _t("liquidateAll", "require(repay <= maxRepay); pool.repay(repay); token.safeTransfer(to, take);", contract="Vault")
    r4 = gate({"mechanism": "missing_bound", "term": "maxRepay", "label": "missing_maxRepay"}, tgt4, siblings=[sib4])
    c4 = r4["post_gate_decision"] == "ADVANCE"
    print(f"  [{'PASS' if c4 else 'FAIL'}] missing_bound kin+shared+downstream -> ADVANCE ({r4['post_gate_decision']})"); ok &= c4
    # 5 computed_unapplied same-function value effect -> ADVANCE
    tgt5 = _t("settle", "uint penalty = wmul(repay, rate); token.safeTransfer(to, take);", contract="Vault")
    r5 = gate({"mechanism": "omitted_term", "term": "penalty", "label": "omitted_penalty"}, tgt5)
    c5 = r5["post_gate_decision"] == "ADVANCE"
    print(f"  [{'PASS' if c5 else 'FAIL'}] computed_unapplied same-fn -> ADVANCE ({r5['post_gate_decision']})"); ok &= c5
    # 6 computed term only in sibling (not local) -> not ADVANCE
    tgt6 = _t("settle", "token.safeTransfer(to, take);", contract="Vault")
    r6 = gate({"mechanism": "omitted_term", "term": "penalty", "label": "omitted_penalty"}, tgt6,
              siblings=[_t("other", "uint penalty = wmul(x, r);", contract="Vault")])
    c6 = r6["post_gate_decision"] != "ADVANCE"
    print(f"  [{'PASS' if c6 else 'FAIL'}] computed-in-sibling-only -> not ADVANCE ({r6['post_gate_decision']})"); ok &= c6
    # 7 sibling-delta still requires P34: recipient parity present -> ADVANCE; absent -> not
    tgt7 = _t("claim_many", "address o = escrow.ownerOf(id); token.transfer(o, amt);", contract="Rewards")
    sib7 = _t("claim", "address o = escrow.ownerOf(id); o = avm.getOriginalOwner(id); token.transfer(o, amt);", contract="Rewards")
    r7a = gate({"mechanism": "recipient_missing", "term": "getOriginalOwner", "label": "rec"}, tgt7, siblings=[sib7])
    r7b = gate({"mechanism": "recipient_missing", "term": "getOriginalOwner", "label": "rec"}, tgt7, siblings=[_t("unrelated", "x=1;")])
    c7 = r7a["post_gate_decision"] == "ADVANCE" and r7b["post_gate_decision"] != "ADVANCE"
    print(f"  [{'PASS' if c7 else 'FAIL'}] sibling-delta requires P34 (parity {r7a['post_gate_decision']} / no-parity {r7b['post_gate_decision']})"); ok &= c7
    # 8 no subject identifiers in config
    cfg = CFG.read_text().lower()
    c8 = not any(t in cfg for t in ("sentiment", "erc6909", "plaza", "traitforge", "dittoeth", "basin", "_getvalueof"))
    print(f"  [{'PASS' if c8 else 'FAIL'}] no subject identifiers in config"); ok &= c8
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by run_p45)")


if __name__ == "__main__":
    raise SystemExit(main())
