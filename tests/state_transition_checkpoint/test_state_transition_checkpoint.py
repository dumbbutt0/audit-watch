"""P251 — state-transition examine-time checkpoint unit tests (S1-S5 + checkpoint-not-detector invariant)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import state_transition_checkpoint_taxonomy as stc  # noqa: E402

PAT = json.loads((ROOT / "config" / "state_transition_checkpoint_patterns.json").read_text())


def _fams(name, body):
    return {r["state_family"] for r in stc.classify("C", name, "", body, patterns=PAT)}


def test_s1_reset_overwrite_user_state():
    body = "function _lock(address _recipient){ lockedTokens[_recipient].unlockTime = uint32(block.timestamp) + d; }"
    assert "S1_reset_overwrite_user_state" in _fams("_lock", body)


def test_s2_growable_set_unbounded_loop():
    body = "function pause(){ _liveProposals.add(id); for (uint i; i < proposals.length; i++){ delete timestamps[p]; } }"
    assert "S2_growable_set_unbounded_loop" in _fams("pause", body)


def test_s3_dual_state_inconsistency():
    body = "function approveUSDPrice(){ usdUpdateProposal.approvals[msg.sender] = id; approvalsCount++; }"
    assert "S3_dual_state_inconsistency" in _fams("approveUSDPrice", body)


def test_s4_branch_consequence_not_traced():
    body = "function onOFTReceived(){ if (weth.balanceOf(address(this)) < _amount) { dcntEth.transfer(_to, _amount); return; } }"
    assert "S4_branch_consequence_not_traced" in _fams("onOFTReceived", body)


def test_s5_time_window_expiry_interaction():
    body = "function updateExpirationPeriod(uint newPeriod){ expirationPeriod = newPeriod; require(timestamp + expirationPeriod > block.timestamp); }"
    assert "S5_time_window_expiry_interaction" in _fams("updateExpirationPeriod", body)


def test_checkpoint_never_concludes_or_sets_severity():
    body = "function _lock(address _onBehalfOf){ lockedTokens[_onBehalfOf].unlockTime = block.timestamp + duration; }"
    recs = stc.classify("C", "_lock", "", body, patterns=PAT)
    assert recs, "expected at least one reasoning record"
    for r in recs:
        assert r["severity"] is None and r["confidence"] is None
        assert r["concluded"] is False and r["requires_operator_reasoning"] is True
        assert r["output_type"] == "reasoning_record"
        assert r["exploit_hypothesis"] == "" and r["post_state"] == ""
        assert len(r["questions"]) == 8


def test_benign_cei_correct_state_update_no_record():
    """A CEI-correct standard ERC20 transfer (a real state update) produces no record, and a plain view getter
    produces none — no generic state-change noise."""
    transfer = ("function transfer(address to, uint amt) public returns (bool) {"
                " _balances[msg.sender] -= amt; _balances[to] += amt; emit Transfer(msg.sender,to,amt);"
                " return true; }")
    assert _fams("transfer", transfer) == set()
    assert _fams("getOwner", "function getOwner() public view returns (address){ return _owner; }") == set()


def test_only_five_families_exist():
    assert set(stc.FAMILIES) == {
        "S1_reset_overwrite_user_state", "S2_growable_set_unbounded_loop",
        "S3_dual_state_inconsistency", "S4_branch_consequence_not_traced",
        "S5_time_window_expiry_interaction"}
