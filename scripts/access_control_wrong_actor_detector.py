#!/usr/bin/env python3
"""
access_control_wrong_actor_detector.py — Phase-71 RESEARCH-ONLY + REVIEW-ONLY Access-Control detector (un-wired).

NARROW SCOPE ONLY — the FIRST over-permissive / wrong-actor authorization shape: `post_publication_creator_overreach_v1`.
An authorized CREATOR / ARTIST / PROJECT-OWNER (auth modifier or inline creator check IS present) can mutate
minter/buyer-governing settings AFTER public publication (sale/mint has begun), beyond the safe scope of creator
authority. This is OVER-PERMISSIVE authorization, NOT missing-auth.

Separation from the parked missing-auth detector (scripts/access_control_missing_auth_detector.py — NOT modified here):
- NO authorization present  -> ABSTAIN (belongs to missing-auth, not this family).
- Auth present but actor is owner/admin (globally trusted), a validated contract caller (factory/proxy/module), or the
  caller bound to their OWN resource -> REJECT (not creator overreach).
- Auth present AND actor is a creator/artist/project-owner AND a published, minter-governing setting is mutated -> ADVANCE.

Out of scope (do NOT handle): missing-auth, owner/admin global trust, generic role-too-broad, stale operator after
transfer, delegatecall/multicall bypass, initializer misuse, signature authority, pure resource-id binding mismatch.

Outputs ONLY: REVIEW_ONLY_ADVANCE / REVIEW_ONLY_ABSTAIN / REVIEW_ONLY_REJECTED. Forbidden states CONFIRMED_BUG /
READY_TO_SUBMIT / AUTO_SUBMIT are not in the enum and cannot be emitted. Every output is a HUMAN-REVIEW candidate.

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
Usage: access_control_wrong_actor_detector.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

# real assignment LHS (a = b), excluding ==, <=, >=, != comparisons
_ASSIGN_RE = re.compile(r"([A-Za-z_]\w*(?:\[[^\]]*\])?(?:\.[A-Za-z_]\w*(?:\[[^\]]*\])?)*)\s*=(?!=)")

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "access_control_wrong_actor_detector.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # strip_comments  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}
DETECTOR = "post_publication_creator_overreach_v1"


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


def _is_test_mock(candidate) -> bool:
    f = (candidate.get("file", "") or "").lower()
    return any(s in f for s in ("/test", "/mock", "/demo", ".t.sol", "mock"))


def _classify_auth(candidate, body) -> tuple[bool, str, str]:
    """Return (present, actor_class, evidence). actor_class in creator / owner_admin / caller_validation / self_resource / none."""
    c = _cfg()
    low = body.lower()
    for m in _mods(candidate):
        ml = m.lower()
        if any(t in ml for t in c["creator_actor_terms"]):
            return True, "creator", f"modifier '{m}'"
        if any(t in ml for t in c["caller_validation_actor_terms"]):
            return True, "caller_validation", f"modifier '{m}'"
        if any(t in ml for t in c["owner_admin_actor_terms"]):
            return True, "owner_admin", f"modifier '{m}'"
    # inline check (no qualifying modifier)
    if any(ctx in low for ctx in c["inline_auth_context"]) and ("msg.sender" in low or "_msgsender(" in low):
        if any(t in low for t in c["creator_inline_terms"]):
            return True, "creator", "inline msg.sender vs creator/artist"
        if any(t in low for t in c["resource_owner_inline_terms"]):
            return True, "self_resource", "inline msg.sender vs resource owner (ownerOf/balanceOf/approval)"
        if any(t in low for t in c["owner_inline_terms"]):
            return True, "owner_admin", "inline msg.sender vs owner()/admin"
        return True, "self_resource", "inline msg.sender self-binding"
    if _mods(candidate):
        return True, "owner_admin", f"modifier '{_mods(candidate)[0]}' (unclassified -> treated as non-creator/trusted)"
    return False, "none", ""


def _assigned_lhs(body) -> str:
    """Lower-cased join of all assignment LHS targets (writes only, not reads/guards)."""
    return " ".join(m.group(1).lower() for m in _ASSIGN_RE.finditer(body))


def _user_facing_settings(lhs_joined) -> list:
    c = _cfg(); out = []
    for kind, terms in c["user_facing_setting_signals"].items():
        for t in terms:
            if t in lhs_joined:  # the setting must be WRITTEN (appears in an assignment LHS), not merely read
                out.append({"setting": t, "kind": kind, "evidence": f"assignment mutates '{t}'"})
                break
    return out


def detect(candidate: dict, siblings=None) -> dict:
    c = _cfg(); D = c["decisions"]
    raw_low = (candidate.get("snippet", "") or "").lower()  # keep comments for NatSpec/intent evidence
    body = _strip(candidate.get("snippet", "")); low = body.lower()
    vis = (candidate.get("visibility", "") or "").lower()
    mut = (candidate.get("mutability", "") or "").lower()

    base = {**FLAGS, "candidate_id": candidate.get("candidate_id") or f"{candidate.get('contract')}.{candidate.get('function')}",
            "detector": DETECTOR,
            "target": {"file": candidate.get("file"), "contract": candidate.get("contract"),
                       "function": candidate.get("function"), "lines": candidate.get("lines", "")},
            "human_review_required": True}

    def out(decision, **kw):
        row = {**base, **kw, "decision": decision}
        row.setdefault("existing_authorization", {"present": False, "modifier_or_check": None, "authorized_actor": None, "evidence": None})
        row.setdefault("publication_state", {"present": False, "signals": [], "evidence": None})
        row.setdefault("mutated_user_facing_settings", [])
        row.setdefault("downstream_user_impact", {"paths": [], "evidence": None})
        row.setdefault("over_permission_reason", {"kind": None, "evidence": None})
        row.setdefault("design_absence", {"rejected": False, "reason": None})
        row.setdefault("confidence", "LOW")
        return row

    # 1. caller surface / trivial rejects
    if vis not in c["public_visibilities"]:
        return out(D["abstain"], design_absence={"rejected": True, "reason": f"visibility={vis} (not public/external)"})
    if _is_test_mock(candidate):
        return out(D["rejected"], design_absence={"rejected": True, "reason": "test/mock/demo file"})
    if mut in c["view_mutabilities"]:
        return out(D["rejected"], design_absence={"rejected": True, "reason": "view/pure getter (no privileged effect)"})

    # 2. authorization classification (SEPARATION from missing-auth)
    present, klass, auth_ev = _classify_auth(candidate, body)
    if not present:
        return out(D["abstain"], existing_authorization={"present": False, "modifier_or_check": None, "authorized_actor": None,
                   "evidence": "no authorization present"},
                   design_absence={"rejected": True, "reason": "no authorization present -> belongs to the missing-auth detector (not this family)"})
    auth = {"present": True, "modifier_or_check": auth_ev, "authorized_actor": klass, "evidence": auth_ev}
    if klass != "creator":
        reason = {"owner_admin": "authorized actor is owner/admin (globally trusted) -> not creator overreach",
                  "caller_validation": "authorized actor is a validated contract caller (factory/proxy/module) -> not creator overreach",
                  "self_resource": "authorization binds the caller to their OWN resource (correct binding) -> not creator overreach"}[klass]
        return out(D["rejected"], existing_authorization=auth, design_absence={"rejected": True, "reason": reason})

    # actor == creator from here
    # 3. design-absence: explicitly intentionally-mutable creator setting (scan RAW incl. comments/NatSpec)
    if any(s in raw_low for s in c["intentional_mutability_signals"]):
        return out(D["rejected"], existing_authorization=auth,
                   design_absence={"rejected": True, "reason": "creator setting explicitly documented as intentionally mutable at any time"})

    # 4. mutated user-facing settings (must affect minters/buyers; metadata-only is rejected).
    #    Settings must be WRITTEN (assignment LHS) — merely reading endTime in a guard does not count.
    lhs_joined = _assigned_lhs(body)
    settings = _user_facing_settings(lhs_joined)
    if not settings:
        if any(s in lhs_joined for s in c["metadata_only_signals"]):
            return out(D["rejected"], existing_authorization=auth,
                       design_absence={"rejected": True, "reason": "creator metadata-only update (no fee/supply/time/eligibility/recipient/refund user impact)"})
        return out(D["abstain"], existing_authorization=auth,
                   design_absence={"rejected": True, "reason": "no user-facing minter/buyer setting mutated"})

    # 5. publication / public-use state (pre-publication creator setup is in creator scope -> not overreach)
    pub_signals = [s for s in c["publication_signals"] if s in low]
    if not pub_signals:
        return out(D["rejected"], existing_authorization=auth, mutated_user_facing_settings=settings,
                   design_absence={"rejected": True, "reason": "no publication/public-use state (pre-publication creator setup is within creator authority)"})
    pub = {"present": True, "signals": pub_signals, "evidence": f"publication/public-use signals: {pub_signals}"}

    # 6. downstream user-impact path
    paths = [p for p in c["downstream_user_paths"] if p in low]
    minter_kinds = {"fee", "supply", "time_window", "allowlist", "eligibility", "recipient", "refund"}
    minter_settings = [s for s in settings if s["kind"] in minter_kinds]
    if not paths and not minter_settings:
        return out(D["abstain"], existing_authorization=auth, publication_state=pub, mutated_user_facing_settings=settings,
                   design_absence={"rejected": True, "reason": "cannot establish a downstream minter/buyer impact path"})
    dui = {"paths": paths or [s["kind"] for s in minter_settings],
           "evidence": f"downstream paths {paths}" if paths else "setting kind inherently read by the minter/buyer path"}

    # 7. over-permission reason
    if pub_signals and any(s["kind"] in ("time_window", "fee", "supply") for s in settings):
        over = {"kind": "post_publication_boundary", "evidence": "creator mutates fee/supply/time-window settings while a publication/public-use state is present"}
    elif minter_settings:
        over = {"kind": "minter_governing_effect", "evidence": f"creator mutates minter-governing settings {[s['kind'] for s in minter_settings]}"}
    else:
        return out(D["abstain"], existing_authorization=auth, publication_state=pub, mutated_user_facing_settings=settings,
                   downstream_user_impact=dui, design_absence={"rejected": True, "reason": "no over-permission reason established"})

    conf = "HIGH" if (len(minter_settings) >= 2 or any(s["kind"] in ("fee", "supply", "time_window") for s in minter_settings)) else "MEDIUM"
    return out(D["advance"], existing_authorization=auth, publication_state=pub, mutated_user_facing_settings=settings,
               downstream_user_impact=dui, over_permission_reason=over, design_absence={"rejected": False, "reason": None}, confidence=conf)


# --------------------------------- self-test ---------------------------------

def _c(function, snippet, visibility="external", mutability="", modifiers=None, contract="C", file="src/C.sol"):
    return {"function": function, "snippet": snippet, "visibility": visibility, "mutability": mutability,
            "modifiers": modifiers or [], "contract": contract, "file": file}


# WA-A1/A2 anchor body (Phi PhiFactory.updateArtSettings under onlyArtCreator), generalised
_ANCHOR_BODY = ("if (endTime_ < startTime_) revert InvalidTimeRange(); if (endTime_ < block.timestamp) revert EndTimeInPast();"
                "PhiArt storage art = arts[artId_]; if (art.numberMinted > maxSupply_) revert ExceedMaxSupply();"
                "art.receiver = receiver_; art.maxSupply = maxSupply_; art.mintFee = mintFee_; art.startTime = startTime_;"
                "art.endTime = endTime_; art.soulBounded = soulBounded_; art.uri = url_;")


def _self_test():
    ok = True
    ADV, ABS, REJ = "REVIEW_ONLY_ADVANCE", "REVIEW_ONLY_ABSTAIN", "REVIEW_ONLY_REJECTED"
    a1 = detect(_c("updateArtSettings", _ANCHOR_BODY, modifiers=["onlyArtCreator"]))
    c1 = a1["decision"] == ADV
    print(f"  [{'PASS' if c1 else 'FAIL'}] WA-A1/A2 creator post-publication overreach -> ADVANCE ({a1['decision']})"); ok &= c1
    nc7 = detect(_c("_addCredIdPerAddress", "credIdsPerAddress[sender_].push(credId_);", visibility="public"))
    c7 = nc7["decision"] == ABS
    print(f"  [{'PASS' if c7 else 'FAIL'}] WA-NC7 missing-auth (no check) -> ABSTAIN not-this-family ({nc7['decision']})"); ok &= c7
    nc1 = detect(_c("setProtocolFeePercent", "protocolFeePercent = v;", modifiers=["onlyOwner"]))
    c_nc1 = nc1["decision"] == REJ
    print(f"  [{'PASS' if c_nc1 else 'FAIL'}] WA-NC1 onlyOwner -> REJECT ({nc1['decision']})"); ok &= c_nc1
    nc8 = detect(_c("claimFromFactory", "minted[id] = true;", modifiers=["onlyPhiFactory"]))
    c_nc8 = nc8["decision"] == REJ
    print(f"  [{'PASS' if c_nc8 else 'FAIL'}] WA-NC8 caller-validation -> REJECT ({nc8['decision']})"); ok &= c_nc8
    forb = set(_cfg()["decisions"].values()).isdisjoint({"CONFIRMED_BUG", "READY_TO_SUBMIT", "AUTO_SUBMIT"})
    print(f"  [{'PASS' if forb else 'FAIL'}] forbidden output states absent ({forb})"); ok &= forb
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
