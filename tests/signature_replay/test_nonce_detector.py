"""Phase-74 tests for the RESEARCH-ONLY + REVIEW-ONLY signature-replay missing/unconsumed-nonce detector
(missing_or_unconsumed_nonce_in_state_changing_signature_v1, un-wired). Also asserts AC + value-flow modules unaffected."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import signature_replay_nonce_detector as SR  # noqa: E402

ADV, ABS, REJ = "REVIEW_ONLY_ADVANCE", "REVIEW_ONLY_ABSTAIN", "REVIEW_ONLY_REJECTED"


def _c(function, snippet, visibility="external", mutability="", contract="C", file="src/C.sol", verify_context=""):
    return {"function": function, "snippet": snippet, "visibility": visibility, "mutability": mutability,
            "contract": contract, "file": file, "verify_context": verify_context}


SR_A1 = ("(uint256 expiresIn_, address minter_, address ref_, address verifier_, uint256 artId_,, bytes32 data_) = abi.decode(encodeData_, (uint256,address,address,address,uint256,uint256,bytes32));"
         "if (expiresIn_ <= block.timestamp) revert SignatureExpired();"
         "if (_recoverSigner(keccak256(encodeData_), signature_) != phiSignerAddress) revert AddressNotSigned();"
         "_validateAndUpdateClaimState(artId_, minter_, q); _processClaim(artId_, minter_, ref_, verifier_, q);")


def test_1_signature_claim_no_nonce_advances():
    r = SR.detect(_c("signatureClaim", SR_A1))
    assert r["decision"] == ADV
    assert r["defect"]["kind"] == "missing_nonce"
    assert r["signature_verification"]["present"] is True
    assert r["state_changing_effect"]["kind"] in ("claim", "mint")
    assert r["human_review_required"] is True


def test_2_nonce_included_and_consumed_rejects():
    body = "bytes32 h = keccak256(abi.encode(PERMIT_TYPEHASH, owner, spender, value, nonces[owner]++, deadline)); address s = ecrecover(h, v, r, ss); _approve(owner, spender, value);"
    r = SR.detect(_c("permit", body))
    assert r["decision"] == REJ
    assert r["replay_guard"]["nonce_consumed"] is True


def test_3_digest_consumed_rejects():
    body = "bytes32 sh = keccak256(abi.encode(order)); if (hasOffchainOrderBeenFilled[sh]) revert Filled(); address s = ECDSA.recover(sh, sig); hasOffchainOrderBeenFilled[sh] = true; _settle(order);"
    r = SR.detect(_c("fillOrder", body))
    assert r["decision"] == REJ
    assert r["replay_guard"]["digest_consumed"] is True


def test_4_order_claim_id_consumed_rejects():
    body = "bytes32 d = keccak256(abi.encode(claimId, to)); if (claimed[claimId]) revert Used(); address s = ecrecover(d, v, r, ss); claimed[claimId] = true; _mint(to);"
    r = SR.detect(_c("claimWithSig", body))
    assert r["decision"] == REJ


def test_5_deadline_domain_only_not_treated_as_nonce_consumption():
    # deadline + domain present but NO nonce and NO consume mapping -> still missing_nonce ADVANCE; deadline recorded
    body = ("bytes32 d = _hashTypedDataV4(keccak256(abi.encode(MINT_TYPEHASH, to, amount, deadline)));"
            "if (block.timestamp > deadline) revert Expired();"
            "address s = ECDSA.recover(d, sig); require(s == signer); _mint(to, amount);")
    r = SR.detect(_c("mintWithSig", body))
    assert r["decision"] == ADV
    assert r["defect"]["kind"] == "missing_nonce"
    assert r["replay_guard"]["nonce_consumed"] is False
    assert "deadline" in (r["replay_guard"]["evidence"] or "")


def test_6_state_changing_effect_required():
    # signature verified but no state change -> ABSTAIN
    body = "bytes32 d = keccak256(abi.encode(x, y)); address s = ECDSA.recover(d, sig); return s == expected;"
    r = SR.detect(_c("verifyOnly", body))
    assert r["decision"] == ABS


def test_7_view_offchain_signature_rejected():
    body = "bytes32 d = keccak256(abi.encode(x)); return ecrecover(d, v, r, s);"
    r = SR.detect(_c("recoverView", body, mutability="view"))
    assert r["decision"] == REJ


def test_8_test_mock_signature_rejected():
    r = SR.detect(_c("signatureClaim", SR_A1, file="test/MockClaim.t.sol"))
    assert r["decision"] == REJ


def test_9_eip1271_verifier_no_guard_abstains():
    body = "return SignatureChecker.isValidSignatureNow(signer, hash, signature);"
    r = SR.detect(_c("isValidSignatureNow", body))
    assert r["decision"] == ABS  # verifier, no state change


def test_10_field_extraction_encode_and_encodepacked():
    enc = SR.detect(_c("mintWithSig", "bytes32 d = keccak256(abi.encode(MINT_TYPEHASH, to, amount, nonce)); address s = ecrecover(d, v, r, ss); _mint(to, amount);"))
    packed = SR.detect(_c("claimPacked", "bytes32 d = keccak256(abi.encodePacked(to, amount)); address s = ecrecover(d, v, r, ss); _claim(to);"))
    enc_fields = " ".join(enc["signed_payload"]["fields"]).lower()
    packed_fields = " ".join(packed["signed_payload"]["fields"]).lower()
    assert "to" in enc_fields and "amount" in enc_fields and "nonce" in enc_fields
    assert "to" in packed_fields and "amount" in packed_fields
    # nonce present but not consumed -> nonce_not_consumed
    assert enc["defect"]["kind"] == "nonce_not_consumed"


def test_11_forbidden_states_absent():
    decisions = set(SR._cfg()["decisions"].values())
    assert decisions.isdisjoint({"CONFIRMED_BUG", "READY_TO_SUBMIT", "AUTO_SUBMIT"})
    assert SR.FLAGS == {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}
    for r in [SR.detect(_c("signatureClaim", SR_A1)), SR.detect(_c("x", "config = y;"))]:
        assert r["decision"] in (ADV, ABS, REJ)


def test_12_no_production_wiring_and_subject_free_config():
    cfg = (ROOT / "config" / "signature_replay_nonce_detector.json").read_text().lower()
    for banned in ("phi", "secondswap", "ramses", "reserve", "lambowin", "notional", "concrete", "sentiment",
                   "traitforge", "dittoeth", "basin", "blackhole", "bakerfi", "loopfi", "olas", "dyad", "renft", "fenix", "zaros", "arkproject"):
        assert banned not in cfg, banned
    for prod in ("run_pipeline.sh", "scripts/llm_runtime.py", "config/agent_policy.json", "config/runtime_policy.json"):
        p = ROOT / prod
        if p.exists():
            assert "signature_replay_nonce_detector" not in p.read_text()


# ---- P76: call-path-scoped verify context ----
def _callee(function, snippet, contract="C", file="src/C.sol"):
    return {"function": function, "snippet": snippet, "contract": contract, "file": file}


def test_14_internal_helper_verify_advances():
    body = "bytes32 h = keccak256(abi.encode(to, amount)); _validateSig(h, sig); _mint(to, amount);"
    callees = {"_validateSig": _callee("_validateSig", "address s = ecrecover(h, v, r, ss); require(s == signer);")}
    r = SR.detect(_c("mintWithSig", body), callees=callees)
    assert r["decision"] == ADV
    assert r["defect"]["kind"] == "missing_nonce"
    assert r["signature_verification"]["classification"] == "internal_callpath"


def test_15_library_verify_available_advances():
    body = "bytes32 h = keccak256(abi.encode(to, amount)); require(Verification.verify(h, sig, signer)); _mint(to, amount);"
    callees = {"Verification.verify": _callee("verify", "return ecrecover(prefixedHash, v, r, s) == signer;", contract="Verification"),
               "verify": _callee("verify", "return ecrecover(prefixedHash, v, r, s) == signer;", contract="Verification")}
    r = SR.detect(_c("mintWithSig", body), callees=callees)
    assert r["decision"] == ADV
    assert r["signature_verification"]["classification"] == "library_callpath"


def test_16_sibling_verifier_not_called_does_not_advance():
    # a verifier exists in callees but the candidate does NOT call it -> no call edge -> never ADVANCE
    body = "_mint(to, amount);"
    callees = {"_validateSig": _callee("_validateSig", "address s = ecrecover(h, v, r, ss); require(s == signer);")}
    r = SR.detect(_c("freeMint", body), callees=callees)
    assert r["decision"] != ADV
    assert r["decision"] == ABS


def test_17_helper_verify_state_bound_hash_rejects():
    body = ("bytes32 h = keccak256(abi.encode(msg.sender, numToMint, nftsClaimed[msg.sender])); _validateSig(h, sig);"
            "nftsClaimed[msg.sender] += numToMint; _mint(msg.sender, numToMint);")
    callees = {"_validateSig": _callee("_validateSig", "address s = ecrecover(h, v, r, ss); require(s == signer);")}
    r = SR.detect(_c("claimFighters", body), callees=callees)
    assert r["decision"] == REJ
    assert "state-bound" in (r["defect"]["evidence"] or "")


def test_18_helper_verify_digest_consumed_rejects():
    body = "bytes32 h = keccak256(abi.encode(order)); if (used[h]) revert Used(); _validateSig(h, sig); used[h] = true; _settle(order);"
    callees = {"_validateSig": _callee("_validateSig", "address s = ecrecover(h, v, r, ss); require(s == signer);")}
    r = SR.detect(_c("fillOrder", body), callees=callees)
    assert r["decision"] == REJ


def test_19_eip712_revocation_batch_nonce_abstains():
    body = "_validateCommitment(terms); uint256 lienId = _mint(recipient); token.transfer(recipient, amount);"
    callees = {
        "_validateCommitment": _callee("_validateCommitment", "bytes32 h = _encodeStrategyData(s, strategy); address recovered = ecrecover(h, v, r, ss); require(recovered == owner());"),
        "_encodeStrategyData": _callee("_encodeStrategyData", "return keccak256(abi.encode(STRATEGY_TYPEHASH, s.strategistNonce, strategy.deadline, root));"),
    }
    r = SR.detect(_c("commitToLien", body), callees=callees)
    assert r["decision"] == ABS
    assert r["defect"]["kind"] == "nonce_not_consumed"


def test_20_phi_self_contained_anchor_still_advances():
    r = SR.detect(_c("signatureClaim", SR_A1))  # no callees -> same_body verify
    assert r["decision"] == ADV
    assert r["signature_verification"]["classification"] == "same_body"


def test_21_library_verify_gap_abstains():
    # call edge to a verify-named callee but body unavailable -> ABSTAIN (cross-contract/library verify gap), never ADVANCE
    body = "require(Verification.verify(h, sig, signer)); _mint(to, amount);"
    r = SR.detect(_c("mintWithSig", body), callees={})
    assert r["decision"] == ABS
    assert r["defect"]["kind"] == "library_verify_gap"


def test_22_access_control_and_value_flow_unchanged():
    import hashlib
    def h(rel):
        return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16]
    assert h("scripts/access_control_missing_auth_detector.py") == "f9ec0bff8de53cf0"
    assert h("scripts/access_control_wrong_actor_detector.py") == "2337edc2ded25116"
    assert h("scripts/mechanism_advancement_gate.py").startswith("697e72a7")
    assert h("scripts/native_eth_sink_gate.py").startswith("5522e15f")
    assert h("scripts/value_flow_surface.py").startswith("aca9125a")


def test_13_access_control_and_value_flow_modules_unchanged():
    # the new chain must not touch the parked AC detectors or value-flow modules
    def h(rel):
        return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16]
    assert h("scripts/access_control_missing_auth_detector.py") == "f9ec0bff8de53cf0"
    assert h("scripts/access_control_wrong_actor_detector.py") == "2337edc2ded25116"
    assert h("scripts/mechanism_advancement_gate.py").startswith("697e72a7")
    assert h("scripts/native_eth_sink_gate.py").startswith("5522e15f")
    assert h("scripts/value_flow_surface.py").startswith("aca9125a")
