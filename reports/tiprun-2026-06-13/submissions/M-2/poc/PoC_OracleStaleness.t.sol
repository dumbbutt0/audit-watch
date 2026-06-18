// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "forge-std/console.sol";

/// @title PoC (M-2, LOW / defense-in-depth): Oracle has no read-side staleness/max-age and the monotonic-update
///        guard is removed, so the TRUSTED price-update flow can store a stale/regressed price that Risk's margin
///        and liquidation math then trust indefinitely.
///
/// @notice TRUST MODEL (important — this is NOT an unprivileged attack): every write path into the Oracle is
/// privileged. `Oracle.updatePrice` is `onlyAuthorizedCaller` (a registered plugin or the owner); the batch route
/// is `MultiTransactionProcessor.processMultiTransactions` (`onlyTxBatcher`) -> `TransactionProcessor`
/// (`onlyMultiTransactionProcessor`) -> `OraclePlugin` (`onlyTransactionProcessor`). The repo's own
/// `TransactionProcessor.basic.t.sol::testOracleRejectsUnauthorizedCaller` proves a plain EOA reverts. So the
/// actor below is the PRICE-UPDATE AUTHORITY, modelled with `vm.prank(deployer)` (deployer owns the Oracle).
///
/// The defect is two missing READ-SIDE / monotonicity guards, i.e. the system has no defense-in-depth if the
/// trusted update flow ever delivers a stale or out-of-order price (operator delay, chain reorg, backend retry):
///   1. `Oracle.updatePrice` has its `timestamp > current` monotonic guard commented out (Oracle.sol:46-54), so a
///      price can REGRESS to an older timestamp.
///   2. `Oracle.getPrice` returns `exist = (timestamp > 0)` with NO max-age (Oracle.sol:36-39) and
///      `Risk.getAssetValueAndRisk` (Risk.sol:56-69) consumes it with NO staleness check — once stored, a price is
///      used by every margin/liquidation decision forever.
contract PoC_OracleStaleness is TransactionProcessorTestBasic {
    using SyntheticPositionLib for uint256;

    function setUp() public override {
        TransactionProcessorTestBasic.setUp();
        deposit(deployerUid, 3_000);
        setOraclePrice(); // price = 1 * FXP_32_ONE at the current block time
        setFundingIndicesInfo();
        // single risk segment, upperBound (notional cap) = 10_000, risk factor 1x
        setSyntheticAssetsInfo(synthAssetId, 10_000, 1 * FXP_32_ONE);
    }

    /// @dev The price-update AUTHORITY can roll the stored price back to an older timestamp (no monotonic guard),
    /// and the read side never expires it (no max-age). No unprivileged actor is involved.
    function test_PoC_authorityCanRollPriceBackAndItNeverExpires() public {
        uint256 t0 = 1_700_000_000; // a realistic recent unix timestamp
        vm.warp(t0);

        // fresh price @ t0
        vm.prank(deployer);
        oracle.updatePrice(synthAssetId, OraclePrice({price: 100 * FXP_32_ONE, timestamp: t0}));
        (int256 p1, bool ok1) = oracle.getPrice(synthAssetId);
        assertEq(p1, 100 * FXP_32_ONE);
        assertTrue(ok1);
        assertEq(oracle.getCurrentTimestamp(synthAssetId), t0);

        // ROLL BACK: store an OLDER timestamp with a different price — accepted (monotonic guard commented out).
        uint256 olderTs = t0 - 1 hours;
        vm.prank(deployer);
        oracle.updatePrice(synthAssetId, OraclePrice({price: 1 * FXP_32_ONE, timestamp: olderTs}));
        (int256 p2, bool ok2) = oracle.getPrice(synthAssetId);
        assertEq(p2, 1 * FXP_32_ONE, "BUG: oracle accepted an older-timestamp price (no monotonic guard)");
        assertTrue(ok2);
        assertEq(oracle.getCurrentTimestamp(synthAssetId), olderTs, "stored timestamp regressed");

        // NO READ-SIDE STALENESS: advance ~10 years; getPrice still reports the ancient price as valid.
        uint256 future = t0 + 3650 days;
        vm.warp(future);
        assertGt(block.timestamp, t0, "warp must advance time"); // guard: any warp anomaly fails loudly, not silently
        (int256 p3, bool ok3) = oracle.getPrice(synthAssetId);
        assertEq(p3, 1 * FXP_32_ONE);
        assertTrue(ok3, "BUG: a ~10-year-old price is still exist=true; Risk will use it for margin");

        uint256 ageDays = (block.timestamp - olderTs) / 1 days;
        assertGe(ageDays, 3650, "stored price is ~10y old yet still considered valid");
        console.log("rolled-back price (FXP):", uint256(p3));
        console.log("age of stored price at read (days):", ageDays);
    }

    /// @dev DOWNSTREAM IMPACT: a regressed/stale price flips a real solvency decision. An insolvent short reads as
    /// healthy once the price is rolled back, so liquidation is hidden (and a margin check would pass). Sizes stay
    /// BELOW the risk-segment cap so the separate F-2 "Risk: no risk" freeze does not mask this.
    function test_PoC_stalePriceFlipsSolvencyAndHidesLiquidation() public {
        vm.warp(1_700_000_000); // realistic block time so we can store an older oracle timestamp

        // open SHORT 1_000 at price 1: notional 1_000 < cap 10_000; value (3_000-1_000)>0 -> healthy.
        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, -1_000); // SHORT

        AccountPosition memory p = positionManager.getAccountPositionByUID(deployerUid);
        (int256 v0, int256 r0) = riskContract.getAccountPositionStatus(p);
        assertGt(v0, 0, "precondition: short starts solvent");
        assertLe(r0, v0 * FXP_32_ONE, "precondition: short starts healthy");

        // ---- TRUE price rises to 5: short is insolvent (value 3_000 - 5*1_000 = -2_000 < 0). ----
        // notional 5*1_000 = 5_000 < cap 10_000, so the risk engine still evaluates (no freeze).
        vm.prank(deployer);
        oracle.updatePrice(synthAssetId, OraclePrice({price: 5 * FXP_32_ONE, timestamp: block.timestamp}));
        p = positionManager.getAccountPositionByUID(deployerUid);
        (int256 vTrue, int256 rTrue) = riskContract.getAccountPositionStatus(p);
        assertLt(vTrue, 0, "at the true price the account is INSOLVENT (should be liquidatable)");
        rTrue; // (risk value not asserted; insolvency is the signal)

        // ---- STALE/ROLLED-BACK price: authority stores the old price 1 with an OLDER timestamp. ----
        uint256 olderTs = block.timestamp - 1 hours;
        vm.prank(deployer);
        oracle.updatePrice(synthAssetId, OraclePrice({price: 1 * FXP_32_ONE, timestamp: olderTs}));
        p = positionManager.getAccountPositionByUID(deployerUid);
        (int256 vStale, int256 rStale) = riskContract.getAccountPositionStatus(p);

        // The SAME insolvent position now reads as solvent+healthy on the stale price -> liquidation hidden,
        // and a margin/withdraw check would pass. Solvency decision flipped by the oracle alone.
        assertGt(vStale, 0, "BUG: stale price makes the insolvent account look solvent");
        assertLe(rStale, vStale * FXP_32_ONE, "BUG: margin check would PASS on the stale price -> liquidation hidden");

        console.log("account value at TRUE price (insolvent, <0):", vTrue < 0 ? "negative" : "non-negative");
        console.log("account value at STALE price (looks healthy):", uint256(vStale));
    }
}
