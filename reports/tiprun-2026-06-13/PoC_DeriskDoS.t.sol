// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "forge-std/console.sol";

/// @title PoC: Risk.checkValidTransition blocks legitimate de-risking of an unhealthy account (liveness/DoS)
/// @notice The ratio guard at Risk.sol:133 reverts when `initValue*updatedRisk < updatedValue*initRisk`, i.e. when
/// the value/risk ratio *improves*. So an account that is below maintenance margin and tries to REDUCE its position
/// (the legitimate way to recover) is reverted with "PM: val/risk dec" — unless it can close enough in a single step
/// to become fully healthy. A partial de-risk that improves health but stays under margin (the common case with
/// partial orderbook fills) is rejected. All de-risk paths (orderbook trade, deleverage) funnel through the same
/// checkValidTransition gate via FundingApplyLib.applyAndUpdate -> PositionManager.updatePosition.
contract PoC_DeriskDoS is TransactionProcessorTestBasic {
    using SyntheticPositionLib for uint256;

    function setUp() public override {
        TransactionProcessorTestBasic.setUp();
        deposit(deployerUid, 10_000);
        setOraclePrice(); // price = 1 * FXP
        setFundingIndicesInfo();
        setSyntheticAssetsInfo(synthAssetId, 10_000, 2 * FXP_32_ONE); // risk = 2x mark value
    }

    function _status() internal view returns (int256 value, int256 risk) {
        AccountPosition memory p = positionManager.getAccountPositionByUID(deployerUid);
        (value, risk) = riskContract.getAccountPositionStatus(p);
    }

    function test_PoC_cannotPartiallyDeriskUnhealthyAccount() public {
        // ---- open long 5_000, then use F-1 to withdraw down to an UNDER-MARGIN state ----
        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, 5_000);

        Withdrawal memory w = createWithdrawal(deployerUid, deployer, 8_000, 0, PRIVATE_KEY);
        bytes[] memory txs = new bytes[](1);
        txs[0] = getMessage(TYPE_WITHDRAWAL, abi.encode(w));
        executeMultiTransactions(txs); // collateral 10_000 -> 2_000 (F-1)

        (int256 v0, int256 r0) = _status();
        assertGt(r0, v0 * FXP_32_ONE, "precondition: account is under maintenance margin");
        // collateral 2_000, synth 5_000 -> value 7_000*FXP, risk 10_000*FXP^2

        // ---- attempt a FAIR partial de-risk: sell 500 synthetic for 500 collateral (value-neutral, risk DOWN) ----
        // New state would be collateral 2_500 / synth 4_500: value 7_000*FXP (same), risk 9_000*FXP^2 (lower) =>
        // still under margin but strictly healthier. This is exactly the recovery a user/keeper should be allowed.
        vm.prank(deployer);
        vm.expectRevert(bytes("PM: val/risk dec"));
        positionManager.updatePositionInDict(deployerUid, 500, synthAssetId, -500);

        // ---- sanity: the position is unchanged (the de-risk was blocked) ----
        AccountPosition memory p = positionManager.getAccountPositionByUID(deployerUid);
        assertEq(p.assets[0].amount, 5_000, "position still 5_000 - user could not de-risk");

        // ---- contrast: closing ENOUGH to become fully healthy in one step IS allowed ----
        // sell 4_000 synthetic for 4_000 collateral -> collateral 6_000 / synth 1_000:
        // value 7_000*FXP, risk 2_000*FXP^2 <= 7_000*FXP^2 => healthy, so checkValidTransition early-returns.
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 4_000, synthAssetId, -4_000);
        p = positionManager.getAccountPositionByUID(deployerUid);
        assertEq(p.assets[0].amount, 1_000, "large de-risk to a healthy state succeeds");

        console.log("under-margin value (FXP):", v0);
        console.log("under-margin risk (FXP^2):", r0);
    }
}
