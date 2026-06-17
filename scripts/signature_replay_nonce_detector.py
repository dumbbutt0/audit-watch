#!/usr/bin/env python3
"""
signature_replay_nonce_detector.py — Phase-74 RESEARCH-ONLY + REVIEW-ONLY Signature-Replay detector (un-wired).

NARROW SCOPE ONLY — `missing_or_unconsumed_nonce_in_state_changing_signature_v1`: a state-changing action authorized by a
VERIFIED signature whose signed payload has NO nonce (or a nonce that is never consumed) and is NOT protected by an
enforced single-use consume guard (nonce-consume OR a check-gated digest/order/claim mapping).

Separation / out of scope (do NOT handle): domain-separator chainId/verifyingContract bugs, cross-chain replay,
missing-deadline-only, EIP-1271 edge cases, abi.encodePacked collision, wrong-signer authorization. Those ABSTAIN/REJECT.

Decision order (reject-first):
  test/mock -> view/pure -> signature-verification-present? (no -> ABSTAIN, not-this-family)
  -> state-changing-effect? (no -> ABSTAIN, verifier/off-chain) -> effective consume guard? (yes -> REJECT)
  -> defect classification -> ADVANCE.

Critical discriminator (Phi SR-A1 vs SR-NC9): a digest/claim mapping counts as an EFFECTIVE guard ONLY when it is
CHECK-GATED (appears in a require/if-revert), not merely set. Phi `signatureClaim` (digest never consumed) ADVANCES; a
claim that does `if (artMinted[..]) revert; ...` REJECTS. Deadline/domain presence is RECORDED but never a consume guard.

Outputs ONLY: REVIEW_ONLY_ADVANCE / REVIEW_ONLY_ABSTAIN / REVIEW_ONLY_REJECTED. Forbidden states CONFIRMED_BUG /
READY_TO_SUBMIT / AUTO_SUBMIT are not in the enum and cannot be emitted. Every output is a HUMAN-REVIEW candidate.

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
Usage: signature_replay_nonce_detector.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "signature_replay_nonce_detector.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # strip_comments  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}
DETECTOR = "missing_or_unconsumed_nonce_in_state_changing_signature_v1"

# nonce-consumption (single-use) patterns — operate on lowercased body
_NONCE_CONSUME_RES = [
    r"_usenonce", r"usenonce\s*\(",
    r"nonces?\b[^;\n]{0,40}\+\+", r"\+\+\s*nonces?\b",
    r"nonces?\b[^;\n]{0,40}\+=\s*1",
    r"nonces?\b[^;\n]{0,40}=\s*[^;\n]*\+\s*1",
]


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _strip(s: str) -> str:
    return sfp.strip_comments(s or "")


def _is_test_mock(candidate) -> bool:
    f = (candidate.get("file", "") or "").lower()
    return any(s in f for s in ("/test", "/mock", "/demo", ".t.sol", "mock"))


def _signature_verify(body_low, extra_low) -> tuple[bool, str, str]:
    c = _cfg()
    hay = body_low + " " + extra_low
    for sig in c["signature_verify_signals"]:
        if sig in hay:
            return True, c["verify_kind_map"].get(sig, "other"), sig
    return False, "", ""


def _state_change(body_low, name_low="") -> tuple[bool, str, str]:
    c = _cfg()
    hay = body_low + " " + name_low  # the function NAME is also a state-change signal (e.g. signatureClaim/execute)
    for s in c["state_change_signals"]:
        if s in hay:
            return True, c["state_change_kind_map"].get(s, "other"), s
    return False, "", ""


def _signed_fields(body) -> tuple[list, str]:
    """Extract signed-payload field tokens from abi.encode/abi.encodePacked(...) and the LHS of `(...) = abi.decode(...)`."""
    fields, hashexpr = [], ""
    m = re.search(r"keccak256\s*\([^;]*\)", body, re.I)
    if m:
        hashexpr = m.group(0)[:160]
    for em in re.finditer(r"abi\.encode(?:packed)?\s*\(([^;]*?)\)\s*\)", body, re.I):
        fields += [a.strip() for a in em.group(1).split(",") if a.strip()]
    for em in re.finditer(r"abi\.encode(?:packed)?\s*\(([^();]*)\)", body, re.I):
        fields += [a.strip() for a in em.group(1).split(",") if a.strip()]
    for dm in re.finditer(r"\(([^)]*)\)\s*=\s*abi\.decode", body, re.I):
        fields += [a.strip() for a in dm.group(1).split(",") if a.strip()]
    # dedupe, preserve order
    seen, out = set(), []
    for f in fields:
        if f.lower() not in seen:
            seen.add(f.lower()); out.append(f)
    return out, hashexpr


def _has_nonce(fields, body_low) -> bool:
    c = _cfg()
    joined = " ".join(fields).lower()
    return any(t in joined for t in c["nonce_field_terms"]) or any(t in body_low for t in c["nonce_field_terms"])


def _nonce_consumed(body_low) -> tuple[bool, str]:
    for rgx in _NONCE_CONSUME_RES:
        if re.search(rgx, body_low):
            return True, rgx
    return False, ""


def _check_gated_digest_guard(body_low) -> tuple[bool, str]:
    """A digest/order/claim consume mapping counts ONLY when it is CHECK-GATED (same unit as a require/if-revert)."""
    c = _cfg()
    units = re.split(r"[;\n{]", body_low)
    for tok in c["digest_consume_signals"]:
        if tok not in body_low:
            continue
        for u in units:
            if tok in u and any(g in u for g in c["consume_guard_context"]):
                return True, tok
    return False, ""


_CALL_RE = re.compile(r"(?:([A-Za-z_]\w*)\s*\.\s*)?([A-Za-z_]\w*)\s*\(")
_VERIFY_PRIMS = ("ecrecover", "ecdsa.recover", ".recover(", "signaturechecker", "isvalidsignature", "_recoversigner", "toethsignedmessagehash")


def _verify_primitive(body_low) -> str:
    for p in _VERIFY_PRIMS:
        if p in body_low:
            return p
    return ""


def _resolve_call_path(cand_name, body, callees, max_depth):
    """BFS over CONCRETE call edges only (candidate body -> resolved callees, depth<=max_depth). Returns
    (path_entries, provenance, verify_gap). path_entries = [{name, body, classification}] for resolved callees;
    NEVER includes global/sibling context — a callee is admitted only when a real call edge resolves it in `callees`.
    verify_gap = names of verify-named callees whose body is unavailable (cross-contract/library gap)."""
    c = _cfg()
    callees = callees or {}
    vmeths = set(c.get("library_verify_method_names", []))
    entries, provenance, gap, visited = [], [], [], set()
    frontier = [(cand_name, body, 0)]
    while frontier:
        cur_name, cur_body, depth = frontier.pop(0)
        if depth > max_depth:
            continue
        for m in _CALL_RE.finditer(cur_body):
            obj, meth = m.group(1), m.group(2)
            ml = meth.lower()
            keys = ([f"{obj}.{meth}", meth] if obj else [meth])
            callee = next((callees[k] for k in keys if k in callees), None)
            verify_named = ml in vmeths or ml.startswith("_validate") or ml.startswith("_verify") or ml.startswith("_recover")
            if callee:
                cid = f"{callee.get('contract','')}.{callee.get('function', meth)}"
                if cid in visited:
                    continue
                visited.add(cid)
                cb = _strip(callee.get("snippet", ""))
                cls = "library_callpath" if obj else "internal_callpath"
                entries.append({"name": cid, "body": cb, "classification": cls})
                provenance.append({"candidate": cur_name, "callee": meth, "call_expr": m.group(0),
                                   "callee_location": callee.get("file"), "primitive": _verify_primitive(cb.lower()),
                                   "classification": cls})
                if depth + 1 <= max_depth:
                    frontier.append((cid, cb, depth + 1))
            elif verify_named:
                gap.append(meth)
                provenance.append({"candidate": cur_name, "callee": meth, "call_expr": m.group(0),
                                   "callee_location": None, "primitive": None, "classification": "unresolved"})
    return entries, provenance, gap


_ASSIGN_BASE_RE = re.compile(r"([A-Za-z_]\w*)\s*(?:\[[^\]]*\])*\s*(?:\+=|-=|=(?!=))")
_TYPE_WORDS = {"uint", "uint256", "int", "int256", "address", "bytes32", "bytes", "bool", "string", "memory", "calldata", "storage"}


def _state_bound(fields, path_low) -> tuple[bool, str]:
    """State-bound-hash replay guard: a signed-payload field that is cumulative-state-like, OR whose base identifier is
    also mutated (assignment LHS) somewhere on the resolved path (e.g. nftsClaimed hashed AND nftsClaimed[..]+=)."""
    c = _cfg()
    fl = " ".join(fields).lower()
    for t in c.get("state_bound_cumulative_signals", []):
        if t in fl:
            return True, f"cumulative-state field '{t}' in signed payload"
    assigned = {a.lower() for a in _ASSIGN_BASE_RE.findall(path_low)}
    for f in fields:
        for bid in re.findall(r"[A-Za-z_]\w*", f.lower()):
            if bid in assigned and bid not in _TYPE_WORDS:
                return True, f"signed field '{f}' base '{bid}' is mutated on the path (state-bound hash)"
    return False, ""


def detect(candidate: dict, siblings=None, callees=None) -> dict:
    c = _cfg(); D = c["decisions"]
    body = _strip(candidate.get("snippet", "")); low = body.lower()
    cand_name = f"{candidate.get('contract')}.{candidate.get('function')}"
    # call-path-scoped resolution: verify/nonce/consume evidence is admitted ONLY from the candidate body or callees
    # reachable via a concrete call edge — never global/sibling/all-contract context (the P75 harness bug is impossible).
    path_entries, provenance, verify_gap = _resolve_call_path(cand_name, body, callees, c.get("call_path_max_depth", 2))
    path_low = " ".join([low] + [e["body"].lower() for e in path_entries])
    vis = (candidate.get("visibility", "") or "").lower()
    mut = (candidate.get("mutability", "") or "").lower()

    base = {**FLAGS, "candidate_id": candidate.get("candidate_id") or f"{candidate.get('contract')}.{candidate.get('function')}",
            "detector": DETECTOR,
            "target": {"file": candidate.get("file"), "contract": candidate.get("contract"),
                       "function": candidate.get("function"), "lines": candidate.get("lines", "")},
            "human_review_required": True}

    def out(decision, **kw):
        row = {**base, **kw, "decision": decision}
        row.setdefault("signature_verification", {"present": False, "kind": None, "classification": None, "evidence": None})
        row.setdefault("signed_payload", {"fields": [], "hash_expression": None, "evidence": None})
        row.setdefault("state_changing_effect", {"kind": None, "evidence": None})
        row.setdefault("replay_guard", {"nonce_in_payload": False, "nonce_consumed": False, "digest_consumed": False,
                                        "claim_or_order_consumed": False, "resource_state_prevents_replay": False, "evidence": None})
        row.setdefault("defect", {"kind": None, "evidence": None})
        row.setdefault("call_path_provenance", provenance)
        row.setdefault("confidence", "LOW")
        return row

    # 1. trivial rejects
    if _is_test_mock(candidate):
        return out(D["rejected"], defect={"kind": "design_absence", "evidence": "test/mock/demo file"})
    if mut in c["view_mutabilities"]:
        return out(D["rejected"], defect={"kind": "design_absence", "evidence": "view/pure getter (no state change)"})

    # 2. signature verification present? (same_body OR a callee resolved via a concrete call edge — NEVER raw context)
    sv, sv_kind, sv_ev = _signature_verify(low, "")
    sv_class = "same_body" if sv else None
    if not sv:
        for e in path_entries:
            s, k, ev = _signature_verify(e["body"].lower(), "")
            if s:
                sv, sv_kind, sv_ev, sv_class = True, k, f"{e['name']}:{ev}", e["classification"]
                break
    if not sv:
        if verify_gap:
            return out(D["abstain"], defect={"kind": "library_verify_gap",
                       "evidence": f"call edge to verify-named callee(s) {sorted(set(verify_gap))} but body unavailable (cross-contract/library verify gap)"})
        return out(D["abstain"], defect={"kind": "design_absence", "evidence": "no signature verification on the candidate's call path -> not this family"})
    sver = {"present": True, "kind": sv_kind, "classification": sv_class, "evidence": sv_ev}

    # 3. state-changing effect present? (path-local)
    sc, sc_kind, sc_ev = _state_change(path_low, (candidate.get("function", "") or "").lower())
    if not sc:
        return out(D["abstain"], signature_verification=sver,
                   defect={"kind": "design_absence", "evidence": "verifier/off-chain only — no state-changing effect on the path"})
    sce = {"kind": sc_kind, "evidence": f"state-change signal '{sc_ev}'"}

    # signed payload over candidate + resolved hash-bearing callees
    fields, hashexpr = _signed_fields(body)
    for e in path_entries:
        ef, eh = _signed_fields(e["body"])
        fields += [x for x in ef if x not in fields]
        hashexpr = hashexpr or eh
    nonce_in = _has_nonce(fields, path_low)
    nonce_cons, nonce_ev = _nonce_consumed(path_low)
    digest_guard, digest_tok = _check_gated_digest_guard(path_low)
    state_bound, sb_ev = _state_bound(fields, path_low)
    deadline_domain = [s for s in c["deadline_domain_signals"] if s in path_low]
    revocation = [s for s in c.get("revocation_batch_signals", []) if s in path_low]

    rg = {"nonce_in_payload": nonce_in, "nonce_consumed": nonce_cons, "digest_consumed": digest_guard,
          "claim_or_order_consumed": digest_guard, "resource_state_prevents_replay": digest_guard or state_bound,
          "evidence": (f"nonce_consume:{nonce_ev}" if nonce_cons else "") + (f" digest_guard:{digest_tok}" if digest_guard else "")
                      + (f" state_bound:{sb_ev}" if state_bound else "")
                      + (f" deadline/domain(recorded):{deadline_domain}" if deadline_domain else "")
                      + (f" revocation/batch(recorded):{revocation}" if revocation else "")}
    sp = {"fields": fields, "hash_expression": hashexpr, "evidence": "signed payload (candidate + call-path)"}

    # 4. effective consume guard -> REJECT
    if nonce_cons:
        return out(D["rejected"], signature_verification=sver, signed_payload=sp, state_changing_effect=sce, replay_guard=rg,
                   defect={"kind": "guarded", "evidence": f"nonce consumed ({nonce_ev}) -> single-use signature"})
    if digest_guard:
        return out(D["rejected"], signature_verification=sver, signed_payload=sp, state_changing_effect=sce, replay_guard=rg,
                   defect={"kind": "guarded", "evidence": f"check-gated digest/order/claim consume mapping '{digest_tok}' prevents replay"})
    # 5. state-bound-hash guard -> REJECT (signed hash binds mutable/cumulative state)
    if state_bound:
        return out(D["rejected"], signature_verification=sver, signed_payload=sp, state_changing_effect=sce, replay_guard=rg,
                   defect={"kind": "guarded", "evidence": f"state-bound hash prevents replay: {sb_ev}"})

    # 6. defect
    if nonce_in:
        # nonce present but not consumed -> ambiguous (often a global revocation / batch nonce) -> ABSTAIN, not a confident ADVANCE
        return out(D["abstain"], signature_verification=sver, signed_payload=sp, state_changing_effect=sce, replay_guard=rg,
                   defect={"kind": "nonce_not_consumed", "evidence": "nonce-like field present but not consumed on the path; "
                           + (f"revocation/batch signals {revocation} present -> reuse may be intended" if revocation else "ambiguous -> human review")})
    # epistemic guard: cannot assert "missing nonce" if the signed payload/hash was never resolved on the path
    # (e.g. signature verified deep in an orchestrator->vault->validate chain but the hash encoder is beyond the call-path
    #  budget). This converges without depth-chasing — verify-found-but-payload-unresolved -> ABSTAIN, never ADVANCE.
    if not fields:
        return out(D["abstain"], signature_verification=sver, signed_payload=sp, state_changing_effect=sce, replay_guard=rg,
                   defect={"kind": "signed_payload_unresolved", "evidence": "signature verified on the call path but the signed payload FIELDS were not resolved within the call-path budget (e.g. nested EIP-712 struct hash deeper than budget) -> cannot assert missing nonce"})
    defect = {"kind": "missing_nonce", "evidence": "no nonce-like field on the signed payload/path and no check-gated consume or state-bound guard"}
    value_kinds = {"mint", "claim", "withdraw", "transfer", "order_fill", "voucher_consume", "settle"}
    conf = "HIGH" if (sc_kind in value_kinds and sv_kind in ("ecrecover", "custom", "ECDSA.recover")) else "MEDIUM"
    return out(D["advance"], signature_verification=sver, signed_payload=sp, state_changing_effect=sce, replay_guard=rg,
               defect=defect, confidence=conf)


# --------------------------------- self-test ---------------------------------

def _c(function, snippet, visibility="external", mutability="", contract="C", file="src/C.sol", verify_context=""):
    return {"function": function, "snippet": snippet, "visibility": visibility, "mutability": mutability,
            "contract": contract, "file": file, "verify_context": verify_context}


# SR-A1 Phi signatureClaim (generalised, real shape)
_SR_A1 = ("(uint256 expiresIn_, address minter_, address ref_, address verifier_, uint256 artId_,, bytes32 data_) = abi.decode(encodeData_, (uint256,address,address,address,uint256,uint256,bytes32));"
          "if (expiresIn_ <= block.timestamp) revert SignatureExpired();"
          "if (_recoverSigner(keccak256(encodeData_), signature_) != phiSignerAddress) revert AddressNotSigned();"
          "_validateAndUpdateClaimState(artId_, minter_, mintArgs_.quantity); _processClaim(artId_, minter_, ref_, verifier_, mintArgs_.quantity, data_, mintArgs_.imageURI, msg.value);")


def _self_test():
    ok = True
    ADV, ABS, REJ = "REVIEW_ONLY_ADVANCE", "REVIEW_ONLY_ABSTAIN", "REVIEW_ONLY_REJECTED"
    a1 = detect(_c("signatureClaim", _SR_A1))
    c1 = a1["decision"] == ADV and a1["defect"]["kind"] == "missing_nonce"
    print(f"  [{'PASS' if c1 else 'FAIL'}] SR-A1 missing-nonce signature claim -> ADVANCE ({a1['decision']})"); ok &= c1
    nc1 = detect(_c("permit", "bytes32 h = keccak256(abi.encode(PERMIT_TYPEHASH, owner, spender, value, _useNonce(owner), deadline)); address s = ECDSA.recover(h, v, r, sig); _approve(owner, spender, value);"))
    c2 = nc1["decision"] == REJ
    print(f"  [{'PASS' if c2 else 'FAIL'}] SR-NC1 permit nonce consumed -> REJECT ({nc1['decision']})"); ok &= c2
    nc7 = detect(_c("fillOrder", "bytes32 sh = keccak256(abi.encode(o)); if (hasOffchainOrderBeenFilled[sh]) revert Filled(); address s = ECDSA.recover(sh, sig); hasOffchainOrderBeenFilled[sh] = true; _settle(o);"))
    c3 = nc7["decision"] == REJ
    print(f"  [{'PASS' if c3 else 'FAIL'}] SR-NC7 digest filled-flag -> REJECT ({nc7['decision']})"); ok &= c3
    nc9 = detect(_c("claim", "if (artMinted[artId][minter]) revert AlreadyClaimed(); address s = _recoverSigner(keccak256(d), sig); _processClaim(artId, minter); artMinted[artId][minter] = true;"))
    c4 = nc9["decision"] == REJ
    print(f"  [{'PASS' if c4 else 'FAIL'}] SR-NC9 artMinted check-gate -> REJECT ({nc9['decision']})"); ok &= c4
    nc8 = detect(_c("isValidSignatureNow", "return ECDSA.recover(hash, signature) == signer;", mutability=""))
    c5 = nc8["decision"] == ABS
    print(f"  [{'PASS' if c5 else 'FAIL'}] SR-NC8 ERC-1271 verifier (no state change) -> ABSTAIN ({nc8['decision']})"); ok &= c5
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
    ap.error("--self-test only (module is a library used by the signature-replay eval runner)")


if __name__ == "__main__":
    raise SystemExit(main())
