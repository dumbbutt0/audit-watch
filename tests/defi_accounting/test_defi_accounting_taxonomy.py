"""
Tests for the DeFi debt/credit conservation taxonomy + detector (deterministic, no LLM/network).

Models cross-function accounting CONSERVATION behind the Zaros Part 2 eval miss cluster (14/16 Highs):
settleVaultsDebt, withdrawUsdTokenFromMarket, getRealizedDebtUsd, recalculateVaultsCreditCapacity,
rebalanceVaultsAssets, AutoDeleverageFactor, WETH reward distribution, usdcAvailableForEngine lockup,
signed/unsigned debt casts, oracle-scaled debt math, global-vs-per-vault totals.

The TWO-SIGNAL GATE (accounting-domain signal AND a state-transition/arith/cast/oracle-scale signal) keeps
the lens FP-tight — NOT a flag-all-'debt'-keyword sweep. Mirrors tests/griefing_dos.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
acct = importlib.import_module("defi_accounting_taxonomy")
audit_mod = importlib.import_module("defi_accounting_audit")


def clf(name, snippet="", file="src/market-making/branches/CreditDelegationBranch.sol",
        contract="CreditDelegationBranch", signature=""):
    return acct.classify(name, signature, file, contract, snippet=snippet)


# ── positive detection (each snippet carries a real accounting transition) ──
def test_settle_vaults_debt():
    c = clf("settleVaultsDebt",
            "vault.marketsRealizedDebtUsd -= ctx.usdcOutX18.intoUint256().toInt256().toInt128(); "
            "UsdTokenSwapConfig.load().usdcAvailableForEngine[vault.engine] += ctx.usdcOutX18.intoUint256();",
            signature="function settleVaultsDebt(uint256[] calldata vaultsIds) external onlyRegisteredSystemKeepers")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)
    assert c["category"] in ("settlement_order", "realized_debt", "debt_credit_conservation", "usdc_lockup", "engine_balance")


def test_withdraw_usd_token_from_market():
    c = clf("withdrawUsdTokenFromMarket",
            "SD59x18 creditCapacityUsdX18 = Market.getCreditCapacityUsd(delegatedCreditUsdX18, marketTotalDebtUsdX18); "
            "market.updateNetUsdTokenIssuance(amountX18.intoSD59x18()); usdToken.mint(msg.sender, amountToMint);",
            signature="function withdrawUsdTokenFromMarket(uint128 marketId, uint256 amount) external onlyRegisteredEngine(marketId)")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)


def test_get_realized_debt_usd():
    c = clf("getRealizedDebtUsd",
            "return sd59x18(self.realizedDebtUsdPerVaultShare).mul(...).add(self.marketsRealizedDebtUsd);",
            file="src/market-making/leaves/Market.sol", contract="Market",
            signature="function getRealizedDebtUsd(Data storage self) internal view returns (SD59x18)")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)


def test_recalculate_vaults_credit_capacity():
    c = clf("recalculateVaultsCreditCapacity",
            "self.marketsRealizedDebtUsd = sd59x18(self.marketsRealizedDebtUsd).add(vaultTotalRealizedDebtChangeUsdX18).intoInt256().toInt128();",
            file="src/market-making/leaves/Vault.sol", contract="Vault",
            signature="function recalculateVaultsCreditCapacity(uint256[] memory vaultsIds) internal")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)


def test_rebalance_vaults_assets():
    c = clf("rebalanceVaultsAssets",
            "inCreditVault.depositedUsdc += usdDelta; inCreditVault.marketsRealizedDebtUsd += usdDelta.toInt256().toInt128(); "
            "inDebtVault.depositedUsdc -= usdDelta; inDebtVault.marketsRealizedDebtUsd -= usdDelta.toInt256().toInt128();",
            signature="function rebalanceVaultsAssets(uint128[2] calldata vaultsIds) external onlyRegisteredSystemKeepers")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)
    assert c["category"] in ("rebalance_accounting", "debt_credit_conservation", "settlement_order")


def test_reward_distribution():
    c = clf("_handleWethRewardDistribution",
            "wethRewardDistribution.distributeValue(amountX18); valuePerShare = total.div(totalShares).mul(amount);",
            file="src/market-making/branches/FeeDistributionBranch.sol", contract="FeeDistributionBranch",
            signature="function _handleWethRewardDistribution(uint128 vaultId, address asset, uint256 amount) internal")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)
    assert c["category"] in ("reward_distribution", "weth_reward")


def test_auto_deleverage_factor():
    c = clf("getAutoDeleverageFactor",
            "return marketTotalDebtUsdX18.sub(thresholdX18).div(scaleX18).mul(adlFactor);",
            file="src/market-making/leaves/Market.sol", contract="Market",
            signature="function getAutoDeleverageFactor(UD60x18 delegatedCredit, SD59x18 totalDebt) internal view returns (UD60x18)")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)
    assert c["category"] in ("auto_deleverage", "pnl_accounting")


def test_usdc_available_for_engine_liquidity():
    c = clf("settleCreditForEngine",
            "UsdTokenSwapConfig.load().usdcAvailableForEngine[engine] += amountX18.intoUint256();",
            file="src/market-making/leaves/UsdTokenSwapConfig.sol", contract="UsdTokenSwapConfig",
            signature="function settleCreditForEngine(address engine, UD60x18 amountX18) internal")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)
    assert c["category"] in ("usdc_lockup", "engine_balance")


def test_signed_debt_cast():
    c = clf("storeDebt",
            "self.marketsRealizedDebtUsd = sd59x18(self.marketsRealizedDebtUsd).add(deltaX18).intoInt256().toInt128();",
            file="src/market-making/leaves/Vault.sol", contract="Vault",
            signature="function storeDebt(Data storage self, SD59x18 deltaX18) internal")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)
    assert c["signed_unsigned"] is True


def test_oracle_scaled_debt_math():
    c = clf("getVaultCreditCapacity",
            "SD59x18 vaultDebtInAssetsX18 = vaultDebtUsdX18.div(assetPriceX18.intoSD59x18()); "
            "uint8 decimalOffset = Constants.SYSTEM_DECIMALS - vault.collateral.decimals; "
            "return vault.collateral.convertSd59x18ToTokenAmount(totalAssetsMinusVaultDebtX18);",
            file="src/market-making/branches/VaultRouterBranch.sol", contract="VaultRouterBranch",
            signature="function getVaultCreditCapacity(uint128 vaultId) public view returns (uint256)")
    assert c["defi_accounting_sensitive"] and acct.is_high_risk(c)
    assert c["oracle_scaled"] is True


def test_global_vs_per_vault_total_update():
    c = clf("updateVaultAndCreditDelegationWeight",
            "creditDelegation.weight = newWeight; self.totalCreditDelegationWeight = newWeight;",
            file="src/market-making/leaves/Vault.sol", contract="Vault",
            signature="function updateVaultAndCreditDelegationWeight(Data storage self, uint128[] memory ids) internal")
    assert c["defi_accounting_sensitive"]
    assert c["category"] in ("global_vs_user_totals", "credit_delegation")


# ── FP controls: must NOT be tagged (no conservation/transition shape) ──
def test_balanceof_getter_not_tagged():
    c = clf("balanceOf", "return _balances[account];", file="src/usd/UsdToken.sol", contract="UsdToken",
            signature="function balanceOf(address account) external view returns (uint256)")
    assert c["defi_accounting_sensitive"] is False


def test_plain_erc20_transfer_helper_not_tagged():
    c = clf("_safeTransfer", "IERC20(token).safeTransfer(to, amount);", file="src/utils/Helper.sol", contract="Helper",
            signature="function _safeTransfer(address token, address to, uint256 amount) internal")
    assert c["defi_accounting_sensitive"] is False


def test_comment_only_debt_mention_not_tagged():
    c = clf("foo", "// this function relates to debt and credit capacity accounting\n return x;",
            file="src/Lib.sol", contract="Lib", signature="function foo() external view returns (uint256)")
    assert c["defi_accounting_sensitive"] is False


def test_admin_config_setter_not_tagged():
    c = clf("configureFeeRecipient",
            "marketMakingEngineConfiguration.protocolFeeRecipients[recipient] = share;",
            file="src/market-making/branches/MarketMakingEngineConfigurationBranch.sol",
            contract="MarketMakingEngineConfigurationBranch",
            signature="function configureFeeRecipient(address recipient, uint256 share) external onlyOwner")
    assert c["defi_accounting_sensitive"] is False


def test_stored_config_view_getter_not_tagged():
    c = clf("getDepositCap", "return Vault.loadExisting(vaultId).depositCap;",
            file="src/market-making/branches/VaultRouterBranch.sol", contract="VaultRouterBranch",
            signature="function getDepositCap(uint128 vaultId) external view returns (uint128)")
    assert c["defi_accounting_sensitive"] is False


def test_local_var_named_credit_no_accounting_update_not_tagged():
    c = clf("pickName", "string memory credit = 'thanks'; return credit;",
            file="src/Misc.sol", contract="Misc",
            signature="function pickName() external pure returns (string memory)")
    assert c["defi_accounting_sensitive"] is False


# ── end-to-end: detector + cross-function invariant resolution ──
def test_detector_and_invariants(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)
    VR = "src/market-making/branches/VaultRouterBranch.sol"
    CD = "src/market-making/branches/CreditDelegationBranch.sol"
    VL = "src/market-making/leaves/Vault.sol"
    manifest = {"items": [
        {"id": "function:CD:settleVaultsDebt#a", "kind": "function", "name": "settleVaultsDebt",
         "contract": "CreditDelegationBranch", "file": CD,
         "signature": "function settleVaultsDebt(uint256[] calldata vaultsIds) external",
         "source_span": {"start_line": 2, "end_line": 2}, "in_scope": True},
        {"id": "function:VL:recalc#b", "kind": "function", "name": "recalculateVaultsCreditCapacity",
         "contract": "Vault", "file": VL,
         "signature": "function recalculateVaultsCreditCapacity(uint256[] memory vaultsIds) internal",
         "source_span": {"start_line": 2, "end_line": 2}, "in_scope": True},
        {"id": "function:VR:getDepositCap#c", "kind": "function", "name": "getDepositCap",
         "contract": "VaultRouterBranch", "file": VR,
         "signature": "function getDepositCap(uint128 vaultId) external view returns (uint128)",
         "source_span": {"start_line": 2, "end_line": 2}, "in_scope": True},
    ]}
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [
            {"manifest_id": "function:CD:settleVaultsDebt#a", "status": "cleared", "clear_reason": "standard settlement"},
            {"manifest_id": "function:VL:recalc#b", "status": "cleared", "clear_reason": "recalc loop"},
        ]}))
    src = {
        CD: ["library CD {",
             "function settleVaultsDebt(uint256[] calldata vaultsIds) external { vault.marketsRealizedDebtUsd -= x.toInt256().toInt128(); UsdTokenSwapConfig.load().usdcAvailableForEngine[e] += x.intoUint256(); }",
             "}"],
        VL: ["library Vault {",
             "function recalculateVaultsCreditCapacity(uint256[] memory ids) internal { self.marketsRealizedDebtUsd = sd59x18(self.marketsRealizedDebtUsd).add(d).intoInt256().toInt128(); }",
             "}"],
        VR: ["library VR {",
             "function getDepositCap(uint128 vaultId) external view returns (uint128) { return Vault.loadExisting(vaultId).depositCap; }",
             "}"],
    }
    for rel, lines in src.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(lines))
    old = sys.argv
    sys.argv = ["defi_accounting_audit"]
    try:
        assert audit_mod.main() == 0
    finally:
        sys.argv = old
    rep = json.loads((tmp_path / "output" / "defi_accounting_audit.json").read_text())
    names = {d["name"] for d in rep["detected"]}
    assert "settleVaultsDebt" in names and "recalculateVaultsCreditCapacity" in names
    assert "getDepositCap" not in names  # stored-config view FP control
    # the previously-cleared high-risk accounting items must surface
    cleared = {x["name"] for x in rep["previously_cleared_high_risk"]}
    assert "settleVaultsDebt" in cleared
    # cross-function invariants present and at least one flagged needs_review
    assert len(rep["cross_function_invariants"]) == 12
    assert any(inv["needs_review"] for inv in rep["cross_function_invariants"])
