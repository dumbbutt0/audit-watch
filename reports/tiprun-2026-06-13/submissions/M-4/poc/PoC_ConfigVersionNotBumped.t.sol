// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "forge-std/console.sol";

/// @title PoC (M-4): setSyntheticAssetsInfo does not bump configVersion, defeating the stale-config batch guard
/// @notice GeneralConfig.setSyntheticAssetsInfo (sets risk-factor segments, oracle signers, quorum, max funding rate)
/// has its incrConfigVersionInternal() commented out (GeneralConfig.sol:179-182), while every OTHER mutator bumps it.
/// MultiTransactionProcessor.processMultiTransactions only reverts a batch when `configVersion < currentVersion`, so
/// changing the most security-relevant config without bumping the version lets in-flight user transactions execute
/// under the new parameters with the stale-config guard never triggering.
contract PoC_ConfigVersionNotBumped is TransactionProcessorTestBasic {
    function test_PoC_setSyntheticAssetsInfo_doesNotBumpConfigVersion() public {
        uint64 v0 = generalConfig.configVersion();

        // change the risk-factor segment (a security-critical parameter) for the synthetic asset
        setSyntheticAssetsInfo(synthAssetId, 10_000, 3 * FXP_32_ONE);
        uint64 v1 = generalConfig.configVersion();
        assertEq(v1, v0, "BUG: configVersion NOT bumped after setSyntheticAssetsInfo (risk params changed silently)");

        // contrast: setMaxFundingRate DOES bump the version (parity the buggy path is missing)
        vm.prank(assetAdmin);
        generalConfig.setMaxFundingRate(synthAssetId, 1 * FXP_32_ONE);
        uint64 v2 = generalConfig.configVersion();
        assertEq(v2, v1 + 1, "control: setMaxFundingRate bumps configVersion");

        console.log("configVersion before setSyntheticAssetsInfo:", v0);
        console.log("configVersion after  setSyntheticAssetsInfo:", v1);
        console.log("configVersion after  setMaxFundingRate     :", v2);
    }
}
