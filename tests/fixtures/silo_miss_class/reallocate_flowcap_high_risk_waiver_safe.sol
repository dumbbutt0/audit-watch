// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// "Safe" pair = a genuinely low-risk view that is NOT a vault-accounting sink (no fund movement, no cap
// mutation, no allocation/flow vocab) and is fine to clear without a per-sink waiver.
contract VaultMetadata {
    string public constant NAME = "SiloVault";

    function version() external pure returns (string memory) {
        return "1.0.0";
    }
}
