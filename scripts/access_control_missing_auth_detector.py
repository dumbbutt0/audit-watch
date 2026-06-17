#!/usr/bin/env python3
"""
access_control_missing_auth_detector.py — Phase-63 RESEARCH-ONLY + REVIEW-ONLY Access-Control detector (un-wired).

NARROW SCOPE ONLY: a public/external privileged-state mutation with NO authorization (no auth modifier AND no inline
msg.sender/role check), corroborated by a protected-sibling / authorized-internal-caller comparand. It does NOT handle
over-permissive/wrong-actor auth (modifier present), delegatecall/multicall bypass, initializer misuse, stale operator
after ownership transfer, signature-authority, hook/callback bypass, or governance — those abstain/reject here.

Outputs ONLY: REVIEW_ONLY_ADVANCE / REVIEW_ONLY_ABSTAIN / REVIEW_ONLY_REJECTED. The forbidden states
CONFIRMED_BUG / READY_TO_SUBMIT / AUTO_SUBMIT are not in the enum and cannot be emitted. Every output is a HUMAN-REVIEW
candidate, never a verdict.

Decision order is reject-first (catch false positives before any advance): caller-surface → design-absence →
authorization-present → privileged-effect → protected-comparand → ADVANCE.

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
Usage: access_control_missing_auth_detector.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "access_control_missing_auth_detector.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # strip_comments  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}
DETECTOR = "missing_auth_public_privileged_mutation_v1"


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _strip(s: str) -> str:
    return sfp.strip_comments(s or "")


def _mods(candidate) -> list:
    m = candidate.get("modifiers", [])
    if isinstance(m, str):
        m = [x.strip() for x in m.split() if x.strip()]
    return [str(x) for x in (m or [])]


def _has_auth_modifier(mods) -> tuple[bool, str]:
    c = _cfg()
    for m in mods:
        ml = m.lower()
        if re.match(c["auth_modifier_regex"], m):
            return True, m
        if any(t in ml for t in c["auth_modifier_terms"]):
            return True, m
    return False, ""


def _has_inline_auth(body) -> tuple[bool, str]:
    c = _cfg()
    low = body.lower()
    # msg.sender / _msgSender used inside a require/if-revert comparison
    if any(ctx in low for ctx in c["inline_auth_context"]) and ("msg.sender" in low or "_msgsender(" in low):
        m = re.search(r"(require\([^;]*msg\.sender[^;]*|if\s*\([^)]*msg\.sender[^)]*\)[^;]*revert[^;]*|msg\.sender[^;]*revert[^;]*)", body, re.I)
        return True, (m.group(0)[:80] if m else "msg.sender authorization check")
    # explicit role / owner / authority / caller-validation checks (delegatecall/proxy context guards count as auth)
    for sig in ("hasrole(", "_checkrole", "_checkowner", "isauthorized", "requiresauth", "authority", "onlyrole",
                "_authorizeupgrade", "delegatecallonly", "onlyproxy"):
        if sig in low:
            return True, sig
    if re.search(r"owner\(\)\s*", low) and any(ctx in low for ctx in c["inline_auth_context"]):
        return True, "owner() check"
    return False, ""


def _is_setup_only(candidate, body, mods) -> bool:
    name = (candidate.get("function", "") or "").lower()
    if name == "constructor":
        return True
    if any(s in [m.lower() for m in mods] for s in ("initializer", "reinitializer")):
        return True
    if "initialize" in name and ("_disableinitializers" in body.lower() or "initializer" in " ".join(mods).lower()):
        return True
    return False


def _is_test_mock(candidate) -> bool:
    f = (candidate.get("file", "") or "").lower()
    return any(s in f for s in ("/test", "/mock", "/demo", ".t.sol", "mock"))


def _permissionless_state_advance(candidate, body) -> tuple[bool, str]:
    """Permissionless-by-design epoch/reward/accumulator state-advance (checkpoint/poke/accrue/...). Context-gated:
    requires the NAME to indicate a state-advance verb AND a body context signal AND NO privileged-admin effect — so an
    admin/role/config/asset-sweep 'checkpoint' is NOT rejected here and stays detectable by the missing-auth path."""
    c = _cfg()
    nl = (candidate.get("function", "") or "").lower()
    low = body.lower()
    name_hit = next((v for v in c.get("permissionless_state_advance_verbs", []) if nl.startswith(v) or nl.startswith("_" + v) or v in nl), None)
    if not name_hit:
        return False, ""
    if not any(ctx in low for ctx in c.get("state_advance_context_signals", [])):
        return False, ""  # name alone is insufficient — require state-advance context
    if any(adm in low for adm in c.get("privileged_admin_effect_signals", [])):
        return False, ""  # admin/role/config/sweep effect -> NOT permissionless-by-design; keep detectable
    return True, f"permissionless_state_advance: '{nl}' advances epoch/reward/accumulator state with no admin/role/config/asset effect"


def _permissionless_position_reduction(candidate, body) -> tuple[bool, str]:
    """Permissionless-by-design CALLER-FUNDED position/debt reduction (repay / burn-on-behalf): the caller burns or
    transfers in their OWN value to REDUCE a target's debt/risk, with NO collateral/protocol asset exiting to the caller
    (or an arbitrary recipient) and NO admin/role/config change. Multi-signal — reduction-intent AND caller-is-source AND
    no value-exit/admin veto — so it is NEVER name-only, and a withdraw/mint/admin/seize path stays detectable.
    Mirrors the DYAD burnDyad false-positive (P66): mint/withdraw is owner-gated, repay/burn is permissionless."""
    c = _cfg()
    nl = (candidate.get("function", "") or "").lower()
    low = body.lower()
    # VETO first: any value/collateral exit, mint, seize, or admin/role/config change -> NOT a pure reduction; keep detectable.
    # ("transfer(" matches OUT transfers incl safeTransfer( but NOT the IN caller-source transferFrom(/safeTransferFrom(.)
    if any(v in low for v in c.get("position_reduction_value_exit_veto", [])):
        return False, ""
    if any(adm in low for adm in c.get("privileged_admin_effect_signals", [])):
        return False, ""
    # (B) caller is the source of the burned/transferred-in value (burn own / pull own / pay own) — required.
    caller_source = (
        bool(re.search(r"(_?burn|burnfrom)\s*\([^;)]*msg\.sender", low)) or
        bool(re.search(r"(safe)?transferfrom\s*\(\s*msg\.sender", low)) or
        any(s in low for s in c.get("caller_funded_source_signals", []))
    )
    if not caller_source:
        return False, ""  # cannot prove caller funds it (e.g. burns someone else's tokens) -> stays detectable
    # (A) reduction intent: a reduction-verb name OR a body liability/debt decrease — required (not name alone; gated by B).
    name_reduce = any(nl.startswith(v) or ("_" + v) in nl or v in nl for v in c.get("position_reduction_verbs", []))
    dsig = c.get("debt_reduction_signals", [])
    debt_decrease = bool(dsig) and bool(re.search(r"(" + "|".join(dsig) + r")\w*\s*(\[[^\]]*\])?\s*-=", low))
    if not (name_reduce or debt_decrease):
        return False, ""
    return True, ("permissionless_position_reduction: caller-funded debt/position reduction "
                  f"'{nl}' (caller burns/transfers in own value to reduce a target's debt; no collateral/asset exits to "
                  "caller, no admin/role/config change) — intentional path asymmetry vs an owner-gated mint/withdraw sibling")


def _permissionless_factory_deploy(candidate, body) -> tuple[bool, str]:
    """Permissionless-by-design factory deployment + self-registration: the caller deploys a NEW instance it controls
    (caller-supplied params) via a source-visible deploy call (create2 / clone / createProxyWithNonce / new C(...)), and
    the freshly-created instance is registered. Not a missing-auth bug. Multi-signal — deploy-name AND deploy-call AND no
    admin/asset/upgrade/module-authority veto — so it is NEVER name-only; a factory that changes global config/roles,
    installs a system module, upgrades an implementation, registers an ARBITRARY existing address (no deploy call), or
    moves existing assets stays detectable. Mirrors reNFT Factory.deployRentalSafe (P68)."""
    c = _cfg()
    nl = (candidate.get("function", "") or "").lower()
    low = body.lower()
    # VETO first: global authority / asset exit / upgrade / module-install -> NOT a benign deploy; keep detectable.
    if any(v in low for v in c.get("factory_deploy_veto", [])):
        return False, ""
    if any(adm in low for adm in c.get("privileged_admin_effect_signals", [])):
        return False, ""
    # (B) source-visible deployment call (create2/clone/createProxyWithNonce/new Contract(...)) — required.
    deploy_call = any(s in low for s in c.get("factory_deploy_call_signals", [])) or bool(re.search(r"\bnew\s+[A-Z]\w*\s*\(", body))
    if not deploy_call:
        return False, ""  # no deploy in THIS call (e.g. arbitrary-registry-add) -> stays detectable
    # (A) deploy/create/clone naming intent — required (deploy-call alone is insufficient; together = two signals).
    if not any(v in nl for v in c.get("factory_deploy_verbs", [])):
        return False, ""
    return True, ("permissionless_factory_deploy: caller deploys a new caller-controlled instance "
                  f"'{nl}' (source-visible deploy call; freshly-created instance registered; no global config/role/"
                  "authority change, no asset transfer, no upgrade) — intentionally open factory entrypoint")


def _design_absence(candidate, body) -> tuple[bool, str]:
    c = _cfg()
    name = (candidate.get("function", "") or "")
    nl = name.lower()
    if (candidate.get("mutability", "") or "").lower() in c["view_mutabilities"]:
        return True, "view/pure getter (no privileged effect)"
    if nl in c["token_standard_fns"]:
        return True, f"standard token primitive '{name}'"
    for v in c["design_absence_permissionless_verbs"]:
        if nl.startswith(v) or nl.startswith("_" + v):
            return True, f"intentionally permissionless/user action '{name}' (verb '{v}')"
    psa, psa_reason = _permissionless_state_advance(candidate, body)
    if psa:
        return True, psa_reason
    ppr, ppr_reason = _permissionless_position_reduction(candidate, body)
    if ppr:
        return True, ppr_reason
    pfd, pfd_reason = _permissionless_factory_deploy(candidate, body)
    if pfd:
        return True, pfd_reason
    return False, ""


def _privileged_effect(body) -> tuple[bool, str, str]:
    c = _cfg()
    low = body.lower()
    for call in c["privileged_effect_calls"]:
        if call in low:
            kind = ("mint_burn" if call in ("_mint", "mint(", "_burn", "burn(")
                    else "pause_control" if "pause" in call
                    else "role_mutation" if "role" in call or "ownership" in call
                    else "asset_movement" if "transfer" in call or "seize" in call or "sweep" in call
                    else "config_mutation")
            return True, kind, call
    # state write: (a) named privileged-state term, or (b) any mapping/array state write (generic governance state)
    for stmt in [s.strip() for s in body.split(";") if s.strip()]:
        sl = stmt.lower()
        if not any(op in stmt for op in ("=", "+=", "-=", ".push(", "delete ")):
            continue
        if "==" in stmt and "=" not in stmt.replace("==", ""):
            continue
        for term in c["privileged_state_terms"]:
            if term in re.sub(r"[^a-z0-9]", "", sl):
                kind = ("privileged_mapping_mutation" if ("[" in stmt or ".push(" in stmt or "delete " in stmt)
                        else "role_mutation" if term in ("role", "owner", "admin", "operator")
                        else "registry_control" if term in ("registry", "whitelist", "blacklist", "allowlist")
                        else "config_mutation")
                return True, kind, stmt[:80]
        # (b) generic mapping/array state write (e.g. someMapping[key].push(x) / delete someMapping[key])
        if c.get("mapping_write_is_privileged") and (".push(" in stmt or stmt.lower().startswith("delete ") or re.search(r"^[A-Za-z_]\w*\s*\[", stmt)):
            return True, "privileged_mapping_mutation", stmt[:80]
    return False, "", ""


def _protected_comparand(candidate, body, siblings) -> tuple[bool, str, dict]:
    c = _cfg()
    name = candidate.get("function", "") or ""
    pe = lambda s: _privileged_effect(_strip(s.get("snippet", "")))[0]
    # (a) sibling with auth that mutates privileged state
    for s in siblings or []:
        sm = _mods(s)
        has_a, _ = _has_auth_modifier(sm)
        if not has_a:
            ia, _ = _has_inline_auth(_strip(s.get("snippet", "")))
            has_a = ia
        if has_a and pe(s):
            return True, "protected_sibling", {"function": s.get("function"), "evidence": f"sibling '{s.get('function')}' has auth + mutates privileged state"}
    # (b) internal-convention name exposed public + any authorized sibling exists
    if name.startswith(c["internal_convention_prefix"]):
        for s in siblings or []:
            sm = _mods(s)
            if _has_auth_modifier(sm)[0] or _has_inline_auth(_strip(s.get("snippet", "")))[0]:
                return True, "protected_internal_caller", {"function": s.get("function"), "evidence": f"`_`-prefixed internal-convention fn declared public; authorized sibling '{s.get('function')}' exists"}
    return False, "", {}


def detect(candidate: dict, siblings=None) -> dict:
    c = _cfg(); D = c["decisions"]
    body = _strip(candidate.get("snippet", ""))
    mods = _mods(candidate)
    vis = (candidate.get("visibility", "") or "").lower()
    base = {**FLAGS, "candidate_id": candidate.get("candidate_id") or f"{candidate.get('contract')}.{candidate.get('function')}",
            "detector": DETECTOR,
            "target": {"file": candidate.get("file"), "contract": candidate.get("contract"), "function": candidate.get("function"),
                       "visibility": vis, "lines": candidate.get("lines", "")},
            "human_review_required": True}

    def out(decision, **kw):
        row = {**base, **kw, "decision": decision}
        row.setdefault("caller_surface", {"reachable": vis in c["public_visibilities"], "evidence": f"visibility={vis}"})
        row.setdefault("privileged_effect", {"kind": "other", "state_or_asset": None, "evidence": None})
        row.setdefault("auth_status", {"has_modifier": False, "has_inline_auth": False, "inline_auth_evidence": None, "auth_rejection_reason": None})
        row.setdefault("comparand", {"kind": None, "file": None, "function": None, "lines": None, "evidence": None})
        row.setdefault("design_absence", {"rejected": False, "reason": None})
        row.setdefault("confidence", "LOW")
        return row

    # 1. caller surface
    if vis not in c["public_visibilities"]:
        return out(D["abstain"], caller_surface={"reachable": False, "evidence": f"visibility={vis} (not public/external)"})
    if _is_test_mock(candidate):
        return out(D["rejected"], design_absence={"rejected": True, "reason": "test/mock/demo file"})
    if _is_setup_only(candidate, body, mods):
        return out(D["rejected"], design_absence={"rejected": True, "reason": "constructor/setup-only (initializer / _disableInitializers)"})

    # 2. authorization present (checked before design-absence so caller-validated callbacks reject via the modifier,
    #    not via an incidental verb match like "claim*")
    hm, hm_ev = _has_auth_modifier(mods)
    hi, hi_ev = _has_inline_auth(body)
    if hm or hi:
        return out(D["rejected"], auth_status={"has_modifier": hm, "has_inline_auth": hi, "inline_auth_evidence": hi_ev or None,
                   "auth_rejection_reason": (f"auth modifier '{hm_ev}'" if hm else f"inline auth: {hi_ev}")})

    # 3. design-absence
    da, da_reason = _design_absence(candidate, body)
    if da:
        return out(D["rejected"], design_absence={"rejected": True, "reason": da_reason})

    # 4. privileged effect
    pe, pe_kind, pe_ev = _privileged_effect(body)
    if not pe:
        return out(D["abstain"], auth_status={"has_modifier": False, "has_inline_auth": False, "inline_auth_evidence": None, "auth_rejection_reason": "no auth (but no privileged effect)"},
                   privileged_effect={"kind": "other", "state_or_asset": None, "evidence": "no privileged state write found"})

    # 5. protected comparand
    pc, pc_kind, pc_info = _protected_comparand(candidate, body, siblings)
    auth_status = {"has_modifier": False, "has_inline_auth": False, "inline_auth_evidence": None, "auth_rejection_reason": None}
    priv = {"kind": pe_kind, "state_or_asset": pe_ev[:60], "evidence": pe_ev}
    if not pc:
        return out(D["abstain"], auth_status=auth_status, privileged_effect=priv,
                   comparand={"kind": None, "file": None, "function": None, "lines": None, "evidence": "no protected comparand (do not advance on missing-modifier alone)"})

    # 6. advance
    conf = "HIGH" if (candidate.get("function", "").startswith("_") and pc_kind == "protected_internal_caller") or pc_kind == "protected_sibling" else "MEDIUM"
    return out(D["advance"], auth_status=auth_status, privileged_effect=priv,
               comparand={"kind": pc_kind, "file": candidate.get("file"), "function": pc_info.get("function"), "lines": "", "evidence": pc_info.get("evidence")},
               confidence=conf)


# --------------------------------- self-test (12 cases) ---------------------------------

def _c(function, snippet, visibility="public", mutability="", modifiers=None, contract="C", file="src/C.sol"):
    return {"function": function, "snippet": snippet, "visibility": visibility, "mutability": mutability,
            "modifiers": modifiers or [], "contract": contract, "file": file}


def _self_test():
    ok = True
    ADV, ABS, REJ = "REVIEW_ONLY_ADVANCE", "REVIEW_ONLY_ABSTAIN", "REVIEW_ONLY_REJECTED"
    onlyowner_sib = _c("setProtocolFeePercent", "protocolFeePercent = v;", modifiers=["onlyOwner"])
    # 1 AC-A1: public privileged mapping mutation, no auth, protected sibling -> ADVANCE
    a1 = detect(_c("_addCredIdPerAddress", "credIdsPerAddress[sender_].push(credId_);"), siblings=[onlyowner_sib])
    c1 = a1["decision"] == ADV
    print(f"  [{'PASS' if c1 else 'FAIL'}] AC-A1 missing-auth+protected-sibling -> ADVANCE ({a1['decision']})"); ok &= c1
    # 2 same-mapping protected sibling corroborates
    sib_same = _c("_removeViaGatedFlow", "credIdsPerAddress[s].pop();", modifiers=["onlyRole"])
    a2 = detect(_c("_removeCredIdPerAddress", "delete credIdsPerAddress[sender_];"), siblings=[sib_same])
    c2 = a2["decision"] == ADV and a2["comparand"]["kind"] in ("protected_sibling", "protected_internal_caller")
    print(f"  [{'PASS' if c2 else 'FAIL'}] same-state protected sibling corroborates ({a2['decision']})"); ok &= c2
    # 3 inline msg.sender check -> REJECTED
    a3 = detect(_c("setConfig", "if (msg.sender != owner) revert NotOwner(); config = x;"), siblings=[onlyowner_sib])
    c3 = a3["decision"] == REJ and a3["auth_status"]["has_inline_auth"]
    print(f"  [{'PASS' if c3 else 'FAIL'}] inline msg.sender check -> REJECTED ({a3['decision']})"); ok &= c3
    # 4 onlyOwner modifier -> REJECTED
    a4 = detect(_c("setSigner", "signer = s;", modifiers=["onlyOwner"]), siblings=[onlyowner_sib])
    c4 = a4["decision"] == REJ and a4["auth_status"]["has_modifier"]
    print(f"  [{'PASS' if c4 else 'FAIL'}] onlyOwner modifier -> REJECTED ({a4['decision']})"); ok &= c4
    # 5 view getter -> REJECTED
    a5 = detect(_c("getRoleAdmin", "return roleAdmin[r];", mutability="view"), siblings=[onlyowner_sib])
    c5 = a5["decision"] == REJ and a5["design_absence"]["rejected"]
    print(f"  [{'PASS' if c5 else 'FAIL'}] view getter -> REJECTED ({a5['decision']})"); ok &= c5
    # 6 permissionless user action -> REJECTED
    a6 = detect(_c("buyShareCred", "shares[msg.sender] += amount; balanceOf[msg.sender]+=x;"), siblings=[onlyowner_sib])
    c6 = a6["decision"] == REJ
    print(f"  [{'PASS' if c6 else 'FAIL'}] permissionless buy -> REJECTED ({a6['decision']})"); ok &= c6
    # 7 setup-only initializer -> REJECTED
    a7 = detect(_c("initialize", "__Ownable_init(o); registry = r;", modifiers=["initializer"]), siblings=[onlyowner_sib])
    c7 = a7["decision"] == REJ and "setup" in (a7["design_absence"]["reason"] or "")
    print(f"  [{'PASS' if c7 else 'FAIL'}] setup-only initializer -> REJECTED ({a7['decision']})"); ok &= c7
    # 8 caller-validated callback (onlyPhiFactory) -> REJECTED
    a8 = detect(_c("claimFromFactory", "minted[id] = true;", modifiers=["onlyPhiFactory"]), siblings=[onlyowner_sib])
    c8 = a8["decision"] == REJ and a8["auth_status"]["has_modifier"]
    print(f"  [{'PASS' if c8 else 'FAIL'}] caller-validated callback -> REJECTED ({a8['decision']})"); ok &= c8
    # 9 token-standard transfer -> REJECTED
    a9 = detect(_c("transferFrom", "balanceOf[to]+=amt; balanceOf[from]-=amt;"), siblings=[onlyowner_sib])
    c9 = a9["decision"] == REJ
    print(f"  [{'PASS' if c9 else 'FAIL'}] token-standard transferFrom -> REJECTED ({a9['decision']})"); ok &= c9
    # 10 over-permissive modifier-present anchor (H-04/H-07) -> REJECTED
    a10 = detect(_c("updateArtSettings", "art.mintFee = f; art.endTime = e;", visibility="external", modifiers=["onlyArtCreator"]), siblings=[onlyowner_sib])
    c10 = a10["decision"] == REJ and a10["auth_status"]["has_modifier"]
    print(f"  [{'PASS' if c10 else 'FAIL'}] over-permissive modifier-present (H-04/H-07) -> REJECTED ({a10['decision']})"); ok &= c10
    # 11 no production wiring + no subject ids in config
    cfgtxt = CFG.read_text().lower()
    banned = ("phi", "cred", "secondswap", "ramses", "reserve", "lambowin", "notional", "concrete", "sentiment", "traitforge", "dittoeth", "basin", "blackhole", "bakerfi", "loopfi")
    no_ids = not any(b in cfgtxt for b in banned)
    for prod in ("run_pipeline.sh", "scripts/llm_runtime.py", "config/agent_policy.json", "config/runtime_policy.json"):
        p = ROOT / prod
        if p.exists() and "access_control_missing_auth_detector" in p.read_text():
            no_ids = False
    print(f"  [{'PASS' if no_ids else 'FAIL'}] no subject ids in config + no production wiring ({no_ids})"); ok &= no_ids
    # 12 forbidden output states absent from enum + flags
    dec = set(_cfg()["decisions"].values())
    c12 = dec.isdisjoint({"CONFIRMED_BUG", "READY_TO_SUBMIT", "AUTO_SUBMIT"}) and FLAGS["review_only"] and FLAGS["research_only"] and not FLAGS["is_gate"]
    print(f"  [{'PASS' if c12 else 'FAIL'}] forbidden states absent + research/review-only flags ({c12})"); ok &= c12
    # bonus: privileged + no comparand -> ABSTAIN (not advance on missing-modifier alone)
    ab = detect(_c("setThing", "config = x;"), siblings=[])
    cb = ab["decision"] == ABS
    print(f"  [{'PASS' if cb else 'FAIL'}] privileged + NO comparand -> ABSTAIN (no advance on missing-modifier alone) ({ab['decision']})"); ok &= cb
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by the access-control eval runner)")


if __name__ == "__main__":
    raise SystemExit(main())
