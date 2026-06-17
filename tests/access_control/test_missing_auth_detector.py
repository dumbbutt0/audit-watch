"""Phase-63 tests for the RESEARCH-ONLY + REVIEW-ONLY narrow missing-auth access-control detector (un-wired)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import access_control_missing_auth_detector as AC  # noqa: E402

ADV, ABS, REJ = "REVIEW_ONLY_ADVANCE", "REVIEW_ONLY_ABSTAIN", "REVIEW_ONLY_REJECTED"


def _c(function, snippet, visibility="public", mutability="", modifiers=None, contract="C", file="src/C.sol"):
    return {"function": function, "snippet": snippet, "visibility": visibility, "mutability": mutability,
            "modifiers": modifiers or [], "contract": contract, "file": file}


ONLYOWNER_SIB = _c("setProtocolFeePercent", "protocolFeePercent = v;", modifiers=["onlyOwner"])


def test_1_public_privileged_mapping_mutation_no_auth_advances():
    r = AC.detect(_c("_addCredIdPerAddress", "credIdsPerAddress[sender_].push(credId_);"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == ADV
    assert r["privileged_effect"]["kind"] == "privileged_mapping_mutation"
    assert r["comparand"]["kind"] in ("protected_sibling", "protected_internal_caller")
    assert r["human_review_required"] is True


def test_2_same_mapping_protected_sibling_corroborates():
    sib = _c("_gatedRemove", "credIdsPerAddress[s].pop();", modifiers=["onlyRole"])
    r = AC.detect(_c("_removeCredIdPerAddress", "delete credIdsPerAddress[sender_];"), siblings=[sib])
    assert r["decision"] == ADV


def test_3_inline_msgsender_check_rejected():
    r = AC.detect(_c("setConfig", "if (msg.sender != owner) revert NotOwner(); config = x;"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ
    assert r["auth_status"]["has_inline_auth"] is True


def test_4_onlyowner_modifier_rejected():
    r = AC.detect(_c("setSigner", "signer = s;", modifiers=["onlyOwner"]), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ
    assert r["auth_status"]["has_modifier"] is True


def test_5_view_getter_rejected():
    r = AC.detect(_c("getRoleAdmin", "return roleAdmin[r];", mutability="view"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ
    assert r["design_absence"]["rejected"] is True


def test_6_permissionless_user_action_rejected():
    r = AC.detect(_c("buyShareCred", "shares[msg.sender] += amount;"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ


def test_7_setup_only_initializer_rejected():
    r = AC.detect(_c("initialize", "__Ownable_init(o); registry = r;", modifiers=["initializer"]), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ
    assert "setup" in (r["design_absence"]["reason"] or "")


def test_8_caller_validated_callback_rejected():
    r = AC.detect(_c("claimFromFactory", "minted[id] = true;", visibility="external", modifiers=["onlyPhiFactory"]), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ
    assert r["auth_status"]["has_modifier"] is True


def test_9_token_standard_transfer_rejected():
    r = AC.detect(_c("transferFrom", "balanceOf[to] += amt; balanceOf[from] -= amt;"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ


def test_10_over_permissive_modifier_present_rejected():
    # H-04/H-07 shape: modifier IS present -> NOT missing-auth -> reject for this detector
    r = AC.detect(_c("updateArtSettings", "art.mintFee = f; art.endTime = e;", visibility="external", modifiers=["onlyArtCreator"]), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ
    assert r["auth_status"]["has_modifier"] is True


def test_11_no_production_wiring_and_no_subject_ids():
    assert AC.FLAGS == {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}
    cfg = (ROOT / "config" / "access_control_missing_auth_detector.json").read_text().lower()
    for banned in ("phi", "cred", "secondswap", "ramses", "reserve", "lambowin", "notional", "concrete", "sentiment", "traitforge", "dittoeth", "basin", "blackhole", "bakerfi", "loopfi"):
        assert banned not in cfg, banned
    for prod in ("run_pipeline.sh", "scripts/llm_runtime.py", "config/agent_policy.json", "config/runtime_policy.json"):
        p = ROOT / prod
        if p.exists():
            assert "access_control_missing_auth_detector" not in p.read_text()


def test_12_forbidden_output_states_absent():
    decisions = set(AC._cfg()["decisions"].values())
    assert decisions.isdisjoint({"CONFIRMED_BUG", "READY_TO_SUBMIT", "AUTO_SUBMIT"})
    # the detector can only ever return one of the three review-only states
    for r in [AC.detect(_c("x", "config = y;"), []), AC.detect(_c("getX", "return x;", mutability="view"), [])]:
        assert r["decision"] in (ADV, ABS, REJ)


def test_13_privileged_no_comparand_abstains_not_advances():
    # must NOT advance on missing-modifier alone (no protected comparand)
    r = AC.detect(_c("setThing", "config = x;"), siblings=[])
    assert r["decision"] == ABS


# ---- P65: permissionless state-advance repair ----
def test_14_checkpoint_reward_accumulator_rejected():
    r = AC.detect(_c("checkpoint", "uint reward = _calculateStakingRewards(); mapServiceInfo[id].reward += reward;"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ
    assert "permissionless_state_advance" in (r["design_absence"]["reason"] or "")


def test_15_epoch_accounting_checkpoint_rejected():
    r = AC.detect(_c("checkpoint", "uint e = epochCounter; mapEpochTokenomics[e].inflation = x;", visibility="external"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ
    assert "permissionless_state_advance" in (r["design_absence"]["reason"] or "")


def test_16_harvest_accrue_permissionless_advance_rejected():
    r1 = AC.detect(_c("accrue", "rewardPerToken += emission * dt; lastUpdate = block.timestamp;"), siblings=[ONLYOWNER_SIB])
    r2 = AC.detect(_c("harvest", "uint reward = _calculate(); totalRewards += reward;"), siblings=[ONLYOWNER_SIB])
    assert r1["decision"] == REJ and r2["decision"] == REJ


def test_17_update_with_admin_config_not_design_absence_rejected():
    # public 'updateConfig' that writes admin/owner -> NOT rejected by permissionless_state_advance
    # (privileged-admin exclusion) -> stays detectable (advances given a protected privileged sibling + no auth)
    priv_sib = _c("setAdmin", "admin = a;", modifiers=["onlyOwner"])
    r = AC.detect(_c("updateConfig", "owner = newOwner; admin = a;"), siblings=[priv_sib])
    assert "permissionless_state_advance" not in (r["design_absence"]["reason"] or "")  # exclusion held
    assert r["decision"] == ADV  # admin/config checkpoint bug remains detectable


def test_18_checkpoint_that_grants_roles_not_rejected_by_name():
    # checkpoint with grantRole -> privileged-admin exclusion -> not design-absence-rejected -> stays detectable
    r = AC.detect(_c("checkpoint", "_grantRole(OPERATOR, msg.sender); rewardIndex += x;"), siblings=[ONLYOWNER_SIB])
    # has inline msg.sender? grantRole uses msg.sender as arg, not an auth check; but to be safe assert it is NOT
    # rejected as permissionless_state_advance
    assert "permissionless_state_advance" not in (r["design_absence"]["reason"] or "")


def test_19_delegatecallonly_counts_as_auth_rejected():
    r = AC.detect(_c("checkpoint", "if (impl == address(0)) revert DelegatecallOnly(); epochReward += x;", visibility="external"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == REJ
    onlyproxy = AC.detect(_c("advanceEpoch", "epoch += 1; reward += x;", modifiers=["onlyProxy"]), siblings=[ONLYOWNER_SIB])
    assert onlyproxy["decision"] == REJ and onlyproxy["auth_status"]["has_modifier"] is True


# ---- P67: permissionless caller-funded position-reduction repair ----
PRIV_SIB = _c("setRegistry", "registry = r;", modifiers=["onlyOwner"])  # auth + privileged effect (registry_control)


def test_20_self_burn_reduces_debt_rejected():
    # caller burns their OWN token to reduce a target's debt -> permissionless-by-design
    r = AC.detect(_c("repay", "token.burn(id, msg.sender, amount);"), siblings=[PRIV_SIB])
    assert r["decision"] == REJ
    assert "permissionless_position_reduction" in (r["design_absence"]["reason"] or "")


def test_21_transferfrom_caller_reduces_debt_rejected():
    r = AC.detect(_c("repay", "debt[id] -= amount; token.transferFrom(msg.sender, address(this), amount);"), siblings=[PRIV_SIB])
    assert r["decision"] == REJ
    assert "permissionless_position_reduction" in (r["design_absence"]["reason"] or "")


def test_22_msg_value_repay_reduces_debt_rejected():
    r = AC.detect(_c("repayWithEth", "debt[id] -= msg.value;"), siblings=[PRIV_SIB])
    assert r["decision"] == REJ
    assert "permissionless_position_reduction" in (r["design_absence"]["reason"] or "")


def test_23_borrow_mint_debt_path_still_detectable():
    # increase-debt path is NOT a reduction (mint veto + no reduction signal) -> stays detectable
    r = AC.detect(_c("borrow", "debt[id] += amount; token.mint(msg.sender, amount);"), siblings=[PRIV_SIB])
    assert r["decision"] == ADV
    assert "permissionless_position_reduction" not in (r["design_absence"]["reason"] or "")


def test_24_withdraw_collateral_path_still_detectable():
    # collateral exits to caller (transfer OUT) -> value-exit veto -> NOT swallowed by the category -> detectable
    r = AC.detect(_c("pullCollateral", "collateral[id] -= amount; token.transfer(msg.sender, amount);"), siblings=[PRIV_SIB])
    assert r["decision"] == ADV
    assert "permissionless_position_reduction" not in (r["design_absence"]["reason"] or "")


def test_25_repay_that_sends_collateral_to_caller_not_rejected():
    # repay that ALSO transfers collateral OUT to caller -> value-exit veto -> NOT rejected as reduction
    r = AC.detect(_c("repay", "debt[id] -= amount; token.transferFrom(msg.sender, address(this), amount); coll.transfer(msg.sender, bonus);"), siblings=[PRIV_SIB])
    assert "permissionless_position_reduction" not in (r["design_absence"]["reason"] or "")


def test_26_arbitrary_burn_of_others_funds_not_rejected():
    # burns SOMEONE ELSE's tokens (no caller-source proof) -> NOT rejected as reduction -> stays detectable
    r = AC.detect(_c("slashBurn", "token.burn(victim, amount);"), siblings=[PRIV_SIB])
    assert "permissionless_position_reduction" not in (r["design_absence"]["reason"] or "")


def test_27_config_admin_change_not_rejected_by_category():
    # caller-funded burn but ALSO changes admin -> admin veto -> NOT rejected as reduction -> stays detectable
    r = AC.detect(_c("repayAndSetAdmin", "debt[id] -= amount; token.burn(id, msg.sender, amount); admin = msg.sender;"), siblings=[PRIV_SIB])
    assert "permissionless_position_reduction" not in (r["design_absence"]["reason"] or "")


def test_28_dyad_burndyad_fixture_rejected():
    # frozen DYAD VaultManagerV2.burnDyad shape (P66 OVERFIT) -> now REJECTED
    sib = _c("mintDyad", "dyad.mint(id, to, amount);", visibility="external", modifiers=["isDNftOwner"])
    r = AC.detect(_c("burnDyad", "dyad.burn(id, msg.sender, amount); emit BurnDyad(id, amount, msg.sender);", visibility="external"), siblings=[sib])
    assert r["decision"] == REJ
    assert "permissionless_position_reduction" in (r["design_absence"]["reason"] or "")


def test_29_ac_a1_still_advances():
    r = AC.detect(_c("_addCredIdPerAddress", "credIdsPerAddress[sender_].push(credId_);"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == ADV


def test_30_no_wiring_and_forbidden_states_absent():
    assert AC.FLAGS == {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}
    decisions = set(AC._cfg()["decisions"].values())
    assert decisions.isdisjoint({"CONFIRMED_BUG", "READY_TO_SUBMIT", "AUTO_SUBMIT"})
    cfg = (ROOT / "config" / "access_control_missing_auth_detector.json").read_text().lower()
    for banned in ("phi", "cred", "secondswap", "ramses", "reserve", "lambowin", "notional", "concrete", "sentiment", "traitforge", "dittoeth", "basin", "blackhole", "bakerfi", "loopfi"):
        assert banned not in cfg, banned
    for prod in ("run_pipeline.sh", "scripts/llm_runtime.py", "config/agent_policy.json", "config/runtime_policy.json"):
        p = ROOT / prod
        if p.exists():
            assert "access_control_missing_auth_detector" not in p.read_text()


# ---- P69: permissionless factory-deploy repair ----
def test_31_createproxy_new_instance_registration_rejected():
    r = AC.detect(_c("deployVault", "address v = factory.createProxyWithNonce(impl, payload, salt); STORE.addVault(v);"), siblings=[PRIV_SIB])
    assert r["decision"] == REJ
    assert "permissionless_factory_deploy" in (r["design_absence"]["reason"] or "")


def test_32_clone_and_new_instance_deploy_rejected():
    r1 = AC.detect(_c("createClone", "address c = implementation.clone(); registry[c] = true;"), siblings=[PRIV_SIB])
    r2 = AC.detect(_c("deployWidget", "Widget w = new Widget(msg.sender); widgets.push(address(w));"), siblings=[PRIV_SIB])
    assert r1["decision"] == REJ and "permissionless_factory_deploy" in (r1["design_absence"]["reason"] or "")
    assert r2["decision"] == REJ and "permissionless_factory_deploy" in (r2["design_absence"]["reason"] or "")


def test_33_arbitrary_registry_add_not_rejected():
    # registers an arbitrary EXISTING address (no deploy call) -> NOT a factory deploy -> stays detectable
    r = AC.detect(_c("addToRegistry", "registry[a] = true;"), siblings=[PRIV_SIB])
    assert "permissionless_factory_deploy" not in (r["design_absence"]["reason"] or "")
    assert r["decision"] == ADV


def test_34_module_deploy_with_global_authority_not_rejected():
    # deploys then installs a system module / grants kernel authority -> veto -> stays detectable
    r = AC.detect(_c("deployModule", "address m = factory.create2(salt, code); kernel.executeAction(Actions.InstallModule, m);"), siblings=[PRIV_SIB])
    assert "permissionless_factory_deploy" not in (r["design_absence"]["reason"] or "")


def test_35_global_config_admin_deploy_not_rejected():
    # deploy that ALSO changes global admin -> admin veto -> NOT rejected as factory deploy
    r = AC.detect(_c("deployAndSetAdmin", "address x = impl.clone(); admin = x;"), siblings=[PRIV_SIB])
    assert "permissionless_factory_deploy" not in (r["design_absence"]["reason"] or "")


def test_36_renft_deployrentalsafe_fixture_rejected():
    body = ("if (threshold == 0 || threshold > owners.length) revert E();"
            "bytes memory data = abi.encodeCall(Factory.initializeRentalSafe, (address(stopPolicy), address(guardPolicy)));"
            "bytes memory initializerPayload = abi.encodeCall(ISafe.setup, (owners, threshold, address(this), data, address(fallbackHandler), address(0), 0, payable(address(0))));"
            "safe = address(safeProxyFactory.createProxyWithNonce(address(safeSingleton), initializerPayload, uint256(keccak256(abi.encode(STORE.totalSafes() + 1, block.chainid)))));"
            "STORE.addRentalSafe(safe); emit Events.RentalSafeDeployment(safe, owners, threshold);")
    sib = _c("configureDependencies", "kernel = k; STORE = Storage(addr);", modifiers=["permissioned"])
    r = AC.detect(_c("deployRentalSafe", body, visibility="external"), siblings=[sib])
    assert r["decision"] == REJ
    assert "permissionless_factory_deploy" in (r["design_absence"]["reason"] or "")


def test_37_ac_a1_still_advances():
    r = AC.detect(_c("_addCredIdPerAddress", "credIdsPerAddress[sender_].push(credId_);"), siblings=[ONLYOWNER_SIB])
    assert r["decision"] == ADV


def test_38_prior_permissionless_regressions_still_rejected():
    # P65 checkpoint + P67 caller-funded reduction must remain rejected
    cp = AC.detect(_c("checkpoint", "uint reward = _calculateStakingRewards(); mapServiceInfo[id].reward += reward;"), siblings=[ONLYOWNER_SIB])
    burn = AC.detect(_c("repay", "token.burn(id, msg.sender, amount);"), siblings=[PRIV_SIB])
    assert cp["decision"] == REJ and burn["decision"] == REJ


def test_39_no_wiring_and_forbidden_states_absent():
    assert AC.FLAGS == {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}
    decisions = set(AC._cfg()["decisions"].values())
    assert decisions.isdisjoint({"CONFIRMED_BUG", "READY_TO_SUBMIT", "AUTO_SUBMIT"})
