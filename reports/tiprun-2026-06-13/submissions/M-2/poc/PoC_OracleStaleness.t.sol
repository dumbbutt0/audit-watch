// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "forge-std/console.sol";

/// @title PoC (M-2): Oracle has no read-side staleness check and the monotonic-update guard is commented out
/// @notice Oracle.updatePrice's `timestamp > current` guard is commented out (Oracle.sol:46-54) and Oracle.getPrice
/// returns exist=true for ANY non-zero timestamp (no max-age). A price can be rolled BACK to an older value and is
/// then consumed forever by Risk's margin math. Demonstrated against the live Oracle used by the perp profile.
contract PoC_OracleStaleness is TransactionProcessorTestBasic {
    function test_PoC_priceCanBeRolledBackAndIsNeverStale() public {
        vm.warp(1_000_000); // set a sane block time so we can move backwards in oracle timestamps

        // current price @ a recent timestamp
        vm.prank(deployer);
        oracle.updatePrice(synthAssetId, OraclePrice({price: 100 * FXP_32_ONE, timestamp: block.timestamp}));
        (int256 p1, bool ok1) = oracle.getPrice(synthAssetId);
        assertEq(p1, 100 * FXP_32_ONE);
        assertTrue(ok1);
        assertEq(oracle.getCurrentTimestamp(synthAssetId), block.timestamp);

        // ROLL BACK: push an OLDER timestamp with a different price — accepted (monotonic guard commented out)
        uint256 olderTs = block.timestamp - 500_000;
        vm.prank(deployer);
        oracle.updatePrice(synthAssetId, OraclePrice({price: 1 * FXP_32_ONE, timestamp: olderTs}));
        (int256 p2, bool ok2) = oracle.getPrice(synthAssetId);
        assertEq(p2, 1 * FXP_32_ONE, "BUG: oracle accepted an older-timestamp price (no monotonic guard)");
        assertTrue(ok2);
        assertEq(oracle.getCurrentTimestamp(synthAssetId), olderTs, "stored timestamp regressed");

        // NO STALENESS: warp far into the future; getPrice still reports the (now ancient) price as valid.
        vm.warp(block.timestamp + 3650 days);
        (int256 p3, bool ok3) = oracle.getPrice(synthAssetId);
        assertEq(p3, 1 * FXP_32_ONE);
        assertTrue(ok3, "BUG: a 10-year-old price is still exist=true; Risk will use it for margin");

        console.log("rolled-back price (FXP):", p3);
        console.log("age of price at read (days):", (block.timestamp - olderTs) / 1 days);
    }
}
