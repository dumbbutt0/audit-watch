"""
Tests for the hostile_token_settlement RESEARCH prototype (must-succeed settlement/cleanup flows where an
attacker-/user-selected token can revert/blacklist/return-false/reenter and block cleanup -> lock/DoS). No LLM,
no network.

8 synthetic fixtures (per the P238 spec) through the pure classifier + a mechanism-based reNFT replay over the real
frozen shadow workspace manifest (recovers PaymentEscrow settle = H-01 family). Recovery is by cleanup-verb +
order-sourced token + missing containment — never answer-key string matching.
"""
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

hts = importlib.import_module("hostile_token_settlement_taxonomy")
audit = importlib.import_module("hostile_token_settlement_audit")


def _c(name, body, sig="", contract="PaymentEscrow"):
    return hts.classify(contract, name, sig, body)


# 1. malicious ERC20 reverts during settlement and blocks reclaim -> ADVANCE (high)
def test_1_malicious_erc20_settle_blocks_reclaim_advances():
    body = """for (uint i; i < order.items.length; i++) {
        Item memory item = order.items[i];
        _safeTransfer(item.token, lender, item.amount);
    }"""
    out = _c("settlePayment", body)
    assert out and out[0]["confidence"] == "high", out
    assert out[0]["finding_shape"] == "hostile_token_settlement_dos"


# 2. allowlisted/trusted token -> REJECT
def test_2_allowlisted_token_rejected():
    body = """require(isSupported[item.token], "bad token");
        _safeTransfer(item.token, lender, item.amount);"""
    assert _c("settlePayment", body) == []


# 3. ERC721/1155 safeTransfer callback reverts during cleanup, blocks unrelated asset return -> ADVANCE
def test_3_erc1155_reclaim_callback_blocks_unrelated_advances():
    body = """for (uint i; i < order.items.length; i++) {
        Item memory item = order.items[i];
        IERC1155(item.token).safeTransferFrom(address(this), lender, item.identifier, item.amount, "");
    }"""
    out = _c("reclaimRentalOrder", body, contract="Reclaimer")
    assert out and out[0]["confidence"] == "high", out


# 4. token failure affects only the caller's own asset -> REJECT
def test_4_caller_own_asset_rejected():
    body = """uint amt = balances[msg.sender];
        balances[msg.sender] = 0;
        token.transfer(msg.sender, amt);"""
    assert _c("withdraw", body) == []


# 5. try/catch isolates the transfer failure -> REJECT
def test_5_trycatch_isolated_rejected():
    body = """try IERC20(item.token).transfer(lender, item.amount) {} catch {
            emit SettleFailed(item.token);
        }"""
    assert _c("settlePayment", body) == []


# 6. pull-payment records debt instead of forcing the push -> REJECT
def test_6_pull_payment_rejected():
    body = """if (!_safeTransfer(item.token, lender, item.amount)) {
            pending[lender][item.token] += item.amount;   // record debt, do not block
        }"""
    assert _c("settlePayment", body) == []


# 7. Seaport-style consideration item chosen by renter can revert during stop/settle -> ADVANCE
def test_7_seaport_consideration_renter_chosen_advances():
    body = """for (uint i; i < consideration.length; i++) {
        _safeTransfer(consideration[i].token, lender, consideration[i].amount);
    }"""
    out = _c("stopRent", body, contract="Stop")
    assert out and out[0]["confidence"] == "high", out


# 8. non-standard ERC20 returns false and caller ignores it; cleanup relies on success -> ADVANCE
def test_8_unchecked_false_return_advances():
    body = """Item memory item = order.items[0];
        IERC20(item.token).transfer(recipient, item.amount);  // return value ignored
        delete positions[id];"""
    out = _c("closePosition", body)
    assert out and out[0]["confidence"] in ("high", "medium"), out


# 8b. admin-only settlement path -> downgrade to LOW
def test_8b_admin_only_downgraded_low():
    body = """require(msg.sender == owner, "onlyOwner");
        for (uint i; i < order.items.length; i++) { _safeTransfer(order.items[i].token, lender, 1); }"""
    out = _c("settlePayment", body)
    assert out and out[0]["confidence"] == "low", out


# ---- P239 campaign regression: admin/self token-rescue FP class (no external counterparty) ----
# blackhole RewardsDistributor.withdrawERC20: owner-gated rescue transferring to msg.sender -> REJECT
def test_p239_owner_rescue_to_msg_sender_rejected():
    body = """require(msg.sender == owner);
        require(_token != address(0));
        uint256 _balance = IERC20(_token).balanceOf(address(this));
        IERC20(_token).transfer(msg.sender, _balance);"""
    assert _c("withdrawERC20", body, sig="address _token", contract="RewardsDistributor") == []


# decent UTBFeeCollector.redeemFees: onlyOwner fee redemption transferring to owner -> REJECT
def test_p239_onlyowner_redeem_to_owner_rejected():
    body = """if (token == address(0)) { payable(owner).transfer(amount); }
        else { IERC20(token).transfer(owner, amount); }"""
    assert _c("redeemFees", body, sig="address token, uint amount", contract="UTBFeeCollector") == []


# ---- mechanism-based reNFT replay (real frozen shadow manifest) ----
def test_renft_replay_recovers_h01_settlement(tmp_path):
    man = ROOT / "audits" / "renft-2024-01-shadow" / "output" / "coverage_manifest.json"
    if not man.exists():
        import pytest
        pytest.skip("reNFT shadow coverage_manifest.json not present (built in P237 replay)")
    out = tmp_path / "renft_replay_audit.json"
    audit._FILE_CACHE.clear()
    sys.argv = ["hostile_token_settlement_audit.py", "--manifest", str(man), "--out", str(out), "--quiet"]
    assert audit.main() == 0

    rep = json.loads(out.read_text())
    assert rep["routed_manifest_ids"] == [] and rep["research_only"] is True and rep["is_gate"] is False
    cands = rep["candidates"]
    byc = {c["contract"]: c for c in cands}
    # H-01 family: PaymentEscrow settlement pushes order-selected item.token with no containment
    assert "PaymentEscrow" in byc, [c["contract"] for c in cands]
    assert byc["PaymentEscrow"]["confidence"] == "high"
    assert byc["PaymentEscrow"]["finding_shape"] == "hostile_token_settlement_dos"
    # low volume, all in the settlement/reclaim family
    assert len(cands) <= 6, f"too many candidates: {[c['contract'] for c in cands]}"
