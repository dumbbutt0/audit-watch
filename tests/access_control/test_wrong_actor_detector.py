"""Phase-71 tests for the RESEARCH-ONLY + REVIEW-ONLY wrong-actor / over-permissive auth detector
(post_publication_creator_overreach_v1, un-wired). Also asserts the parked missing-auth detector is unaffected."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import access_control_wrong_actor_detector as WA  # noqa: E402
import access_control_missing_auth_detector as MA  # parked detector (must stay byte-identical / green)  # noqa: E402

ADV, ABS, REJ = "REVIEW_ONLY_ADVANCE", "REVIEW_ONLY_ABSTAIN", "REVIEW_ONLY_REJECTED"


def _c(function, snippet, visibility="external", mutability="", modifiers=None, contract="C", file="src/C.sol"):
    return {"function": function, "snippet": snippet, "visibility": visibility, "mutability": mutability,
            "modifiers": modifiers or [], "contract": contract, "file": file}


# Phi PhiFactory.updateArtSettings body under onlyArtCreator (WA-A1=H-04, WA-A2=H-07)
ANCHOR_BODY = ("if (endTime_ < startTime_) revert InvalidTimeRange(); if (endTime_ < block.timestamp) revert EndTimeInPast();"
               "PhiArt storage art = arts[artId_]; if (art.numberMinted > maxSupply_) revert ExceedMaxSupply();"
               "art.receiver = receiver_; art.maxSupply = maxSupply_; art.mintFee = mintFee_; art.startTime = startTime_;"
               "art.endTime = endTime_; art.soulBounded = soulBounded_; art.uri = url_;")


def test_1_creator_post_publication_fee_update_advances():
    r = WA.detect(_c("updateArtSettings", ANCHOR_BODY, modifiers=["onlyArtCreator"]))
    assert r["decision"] == ADV
    assert r["existing_authorization"]["authorized_actor"] == "creator"
    assert any(s["kind"] in ("fee", "supply", "time_window") for s in r["mutated_user_facing_settings"])
    assert r["human_review_required"] is True


def test_2_creator_post_publication_eligibility_update_advances():
    body = "require(block.timestamp < endTime); arts[id].verifier = newVerifier; arts[id].allowlist = root;"
    r = WA.detect(_c("setArtEligibility", body, modifiers=["onlyArtCreator"]))
    assert r["decision"] == ADV
    assert any(s["kind"] in ("eligibility", "allowlist") for s in r["mutated_user_facing_settings"])


def test_3_missing_auth_function_not_this_family():
    # no authorization at all -> ABSTAIN (belongs to parked missing-auth detector)
    r = WA.detect(_c("_addCredIdPerAddress", "credIdsPerAddress[sender_].push(credId_);", visibility="public"))
    assert r["decision"] == ABS
    assert r["existing_authorization"]["present"] is False


def test_4_pre_publication_creator_setup_rejected():
    # creator configures their own art record with NO publication/public-use signal -> within creator scope
    body = "arts[id].receiver = r; arts[id].mintFee = f;"
    r = WA.detect(_c("createArtSetup", body, modifiers=["onlyArtCreator"]))
    assert r["decision"] == REJ
    assert "publication" in (r["design_absence"]["reason"] or "")


def test_5_admin_global_owner_setter_rejected():
    r = WA.detect(_c("setProtocolFeePercent", "protocolFeePercent = v;", modifiers=["onlyOwner"]))
    assert r["decision"] == REJ
    assert r["existing_authorization"]["authorized_actor"] == "owner_admin"


def test_6_creator_metadata_only_update_rejected():
    body = "if (block.timestamp < arts[id].endTime) { arts[id].uri = newUri; }"
    r = WA.detect(_c("setArtURI", body, modifiers=["onlyArtCreator"]))
    assert r["decision"] == REJ
    assert "metadata-only" in (r["design_absence"]["reason"] or "")


def test_7_user_owned_self_update_rejected():
    body = "if (ownerOf(id) != msg.sender) revert NotOwner(); profileName[id] = name;"
    r = WA.detect(_c("updateMyProfile", body))
    assert r["decision"] == REJ
    assert r["existing_authorization"]["authorized_actor"] == "self_resource"


def test_8_view_getter_rejected():
    r = WA.detect(_c("getArtMintFee", "return arts[id].mintFee;", mutability="view", modifiers=["onlyArtCreator"]))
    assert r["decision"] == REJ
    assert "view" in (r["design_absence"]["reason"] or "")


def test_9_intentionally_mutable_creator_setting_not_advanced():
    body = "// mintFee can be updated at any time by the creator\n if (block.timestamp < arts[id].endTime) arts[id].mintFee = f;"
    r = WA.detect(_c("updateMintFee", body, modifiers=["onlyArtCreator"]))
    assert r["decision"] != ADV
    assert r["decision"] == REJ


def test_10_forbidden_states_absent():
    decisions = set(WA._cfg()["decisions"].values())
    assert decisions.isdisjoint({"CONFIRMED_BUG", "READY_TO_SUBMIT", "AUTO_SUBMIT"})
    assert WA.FLAGS == {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}
    for r in [WA.detect(_c("updateArtSettings", ANCHOR_BODY, modifiers=["onlyArtCreator"])),
              WA.detect(_c("x", "config = y;"))]:
        assert r["decision"] in (ADV, ABS, REJ)


def test_11_no_production_wiring_and_subject_free_config():
    cfg = (ROOT / "config" / "access_control_wrong_actor_detector.json").read_text().lower()
    # subject ids only; "cred" is intentionally NOT banned here — "creator"/"credential" are generic AC vocabulary
    # essential to this family (not a reference to Phi's Cred.sol subject).
    for banned in ("phi", "secondswap", "ramses", "reserve", "lambowin", "notional", "concrete", "sentiment",
                   "traitforge", "dittoeth", "basin", "blackhole", "bakerfi", "loopfi", "olas", "dyad", "renft", "fenix"):
        assert banned not in cfg, banned
    for prod in ("run_pipeline.sh", "scripts/llm_runtime.py", "config/agent_policy.json", "config/runtime_policy.json"):
        p = ROOT / prod
        if p.exists():
            assert "access_control_wrong_actor_detector" not in p.read_text()


def test_12_missing_auth_detector_unaffected_no_cross_fire():
    # the parked missing-auth detector still ADVANCES AC-A1 and REJECTS the over-permissive anchor (modifier present)
    a1 = MA.detect({"function": "_addCredIdPerAddress", "snippet": "credIdsPerAddress[sender_].push(credId_);",
                    "visibility": "public", "modifiers": [], "contract": "Cred", "file": "src/Cred.sol"},
                   siblings=[{"function": "setProtocolFeePercent", "snippet": "protocolFeePercent = v;", "modifiers": ["onlyOwner"]}])
    assert a1["decision"] == ADV
    over = MA.detect({"function": "updateArtSettings", "snippet": ANCHOR_BODY, "visibility": "external",
                      "modifiers": ["onlyArtCreator"], "contract": "PhiFactory", "file": "src/PhiFactory.sol"}, siblings=[])
    assert over["decision"] == REJ  # missing-auth rejects (modifier present) -> no cross-fire
    # and the wrong-actor detector does NOT advance the missing-auth anchor
    wa_a1 = WA.detect(_c("_addCredIdPerAddress", "credIdsPerAddress[sender_].push(credId_);", visibility="public"))
    assert wa_a1["decision"] != ADV
