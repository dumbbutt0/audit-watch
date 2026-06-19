// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "forge-std/console.sol";

/// @title PoC (M-4): setSyntheticAssetsInfo does not bump configVersion, so the stale-config batch guard is bypassed
/// @notice GeneralConfig.setSyntheticAssetsInfo (sets risk-factor segments, oracle signers, quorum, max funding rate)
/// has its incrConfigVersionInternal() commented out (GeneralConfig.sol:182), while every OTHER mutator bumps it.
/// MultiTransactionProcessor.processMultiTransactions reverts a batch only when `configVersion < currentVersion`
/// (MultiTransactionProcessor.sol:59). So changing the most security-relevant config without bumping the version lets
/// an in-flight user batch — signed/queued against the OLD config — still execute, with the stale-config guard that
/// protects users from mid-flight parameter changes never firing.
contract PoC_ConfigVersionNotBumped is TransactionProcessorTestBasic {
    /// Submit a 1-tx batch (a fresh account registration) carrying an explicit `batchVersion`, via the real
    /// txBatcher relay path. The version-mismatch guard runs BEFORE any tx is processed, so the registration is
    /// merely a valid carrier — what is under test is whether the guard accepts/rejects the stale batch.
    function _submitBatchAtVersion(uint64 uid, uint256 key, uint64 batchVersion) internal {
        bytes[] memory txs = new bytes[](1);
        txs[0] = getMessage(
            TYPE_REGISTER_ACCOUNT,
            abi.encode(createRegisterAccount(uid, vm.addr(key), new SignerInit[](0), key))
        );
        vm.prank(deployer);
        multiTransactionProcessor.processMultiTransactions(txs, batchVersion);
    }

    function _submitBatchAtVersionExpectStale(uint64 uid, uint256 key, uint64 batchVersion) internal {
        bytes[] memory txs = new bytes[](1);
        txs[0] = getMessage(
            TYPE_REGISTER_ACCOUNT,
            abi.encode(createRegisterAccount(uid, vm.addr(key), new SignerInit[](0), key))
        );
        vm.prank(deployer);
        vm.expectRevert(abi.encodeWithSignature("Error(string)", "MultiTransactionProcessor: config version mismatch"));
        multiTransactionProcessor.processMultiTransactions(txs, batchVersion);
    }

    function test_PoC_setSyntheticAssetsInfo_doesNotBumpConfigVersion_bypassesStaleGuard() public {
        uint64 v0 = generalConfig.configVersion();

        // (L2) change a SECURITY-CRITICAL parameter (the risk-factor segment) for the synthetic asset.
        setSyntheticAssetsInfo(synthAssetId, 10_000, 3 * FXP_32_ONE);
        uint64 v1 = generalConfig.configVersion();
        assertEq(v1, v0, "BUG: configVersion NOT bumped after setSyntheticAssetsInfo (risk params changed silently)");

        // (L3) a user batch carrying the STALE version v0 STILL executes after that risk-param change — the
        // stale-config guard never fires, so the batch runs under the NEW risk parameters it never agreed to.
        _submitBatchAtVersion(5001, 0xC0DE01, v0); // ACCEPTED despite the risk change

        // Control + L3 contrast: a NORMAL mutator DOES bump the version...
        vm.prank(assetAdmin);
        generalConfig.setMaxFundingRate(synthAssetId, 1 * FXP_32_ONE);
        uint64 v2 = generalConfig.configVersion();
        assertEq(v2, v1 + 1, "control: setMaxFundingRate bumps configVersion");

        // ...and now the SAME stale batch (configVersion == v0) is correctly REJECTED. The only difference between
        // this rejection and the acceptance above is which config mutator ran — proving the protection exists and
        // is silently missing for the most security-critical one.
        _submitBatchAtVersionExpectStale(5002, 0xC0DE02, v0);

        console.log("configVersion before setSyntheticAssetsInfo:", v0);
        console.log("configVersion after  setSyntheticAssetsInfo:", v1);
        console.log("configVersion after  setMaxFundingRate     :", v2);
    }
}
