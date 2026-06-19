// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "forge-std/console.sol";

/// @title PoC (N-2 / PC-01): Capability registry silently falls back to no-op checks when a provider is missing
/// @notice `PositionManager._marginCheck()` returns a no-op `NullMarginCheck` whenever
/// `capabilityProvider(CAP_MARGIN_CHECK) == address(0)` (PositionManager.sol:76-80), and `registerPlugin` never
/// enforces that a margin provider exists (no plugin declares it as a required capability). So a deployment that
/// is missing / has not yet wired the perp Risk provider accepts undercollateralized position transitions that the
/// real maintenance-margin check would reject. This PoC drops the CAP_MARGIN_CHECK provider (the exact "not wired"
/// state) and opens a deeply insolvent position that is accepted unconditionally.
contract PoC_CapabilityRegistryNoop is TransactionProcessorTestBasic {
    function setUp() public override {
        TransactionProcessorTestBasic.setUp();
        deposit(deployerUid, 1_000);
        setOraclePrice();            // price = 1 * FXP
        setFundingIndicesInfo();
        // large risk-segment cap so getRiskFactor stays valid — isolates the margin NO-OP from the F-2 freeze.
        setSyntheticAssetsInfo(synthAssetId, 1_000_000, 1 * FXP_32_ONE);
    }

    function test_PoC_missingMarginProviderAcceptsInsolventPosition() public {
        // precondition: a real CAP_MARGIN_CHECK provider (perp Risk) is wired by the base harness.
        assertTrue(
            transactionProcessor.capabilityProvider(CAP_MARGIN_CHECK) != address(0),
            "precondition: a margin-check provider is wired"
        );

        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);

        // Simulate the finding's condition: the deployment is missing the CAP_MARGIN_CHECK provider.
        // registerPlugin never required it; unregistering the only provider clears it with no guard.
        vm.prank(deployer);
        transactionProcessor.unregisterPlugin(address(riskPlugin));
        assertEq(
            transactionProcessor.capabilityProvider(CAP_MARGIN_CHECK), address(0),
            "CAP_MARGIN_CHECK provider is now absent -> _marginCheck() falls back to NullMarginCheck"
        );

        // Open a short far exceeding collateral. With the real Risk margin check this is rejected; with the
        // NullMarginCheck no-op it is accepted unconditionally.
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, -5_000); // short 5_000 vs 1_000 collateral

        // Measure with the still-deployed Risk contract (a view; not the gate): the accepted account is insolvent.
        AccountPosition memory p = positionManager.getAccountPositionByUID(deployerUid);
        (int256 value, int256 risk) = riskContract.getAccountPositionStatus(p);
        assertLt(value, 0, "BUG: an INSOLVENT position was accepted because CAP_MARGIN_CHECK silently no-op'd");
        risk; // (insolvency is the signal)

        console.log("accepted account value at true price (FXP, negative = insolvent):",
            value < 0 ? "negative" : "non-negative");
        console.log("synthetic short held with no maintenance-margin enforcement:",
            uint256(int256(-positionManager.getSyntheticBalance(deployerUid, synthAssetId))));
    }
}
