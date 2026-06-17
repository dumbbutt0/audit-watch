// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.Liquidate.t.sol";
import "forge-std/console.sol";

/// @title PoC (M-3): Liquidation has no on-chain maintenance-margin precondition
/// @notice LiquidateTransLib.process never checks that the target is below maintenance margin before force-resizing
/// its position. It reuses the project's own liquidate harness (TransactionProcessorLiquidateTest) to liquidate a
/// demonstrably HEALTHY account: the target (cOwner) holds 100 collateral and a tiny long of 1 (risk << value), yet
/// the liquidation succeeds and seizes/forces the trade. Gated only by onlyTxBatcher, so it is operator-trust
/// dependent — but the on-chain safety that "only unhealthy accounts can be liquidated" is absent.
contract PoC_NoLiquidatablePrecondition is TransactionProcessorLiquidateTest {
    function test_PoC_canLiquidatePerfectlyHealthyAccount() public {
        // Give the target a tiny long position; it keeps its full 100 collateral => clearly healthy.
        _primeLiquidatedSynthetic(1);

        AccountPosition memory before = positionManager.getAccountPositionByUID(cOwnerUid);
        (int256 v, int256 r) = riskContract.getAccountPositionStatus(before);
        // PROVE the target is healthy (risk <= value * FXP) — i.e. NOT liquidatable in any sane margin system.
        assertLe(r, v * FXP_32_ONE, "precondition: target account is healthy / over-collateralized");
        assertEq(before.collateralAmount, cOwnerStartingBalance, "target has full collateral");

        // Liquidate the healthy account anyway — succeeds with no 'not liquidatable' guard.
        Liquidate memory liquidate = _buildLiquidate(true, synthAssetId, 1, cOwnerUid, 1, 1, 1);
        _processThroughMulti(liquidate);

        AccountPosition memory afterPos = positionManager.getAccountPositionByUID(cOwnerUid);
        // The healthy account's position was force-closed and its collateral changed by the forced trade.
        assertEq(afterPos.assets.length, 0, "BUG: healthy account's position force-liquidated");
        assertEq(afterPos.collateralAmount, cOwnerStartingBalance + 1, "forced trade settled against the target");

        console.log("healthy target value (FXP):", v);
        console.log("healthy target risk  (FXP^2):", r);
        console.log("liquidated despite being healthy: position length now", afterPos.assets.length);
    }
}
