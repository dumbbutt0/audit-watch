// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// VALID dominance: the sensitive op `_apply` is INTERNAL and the ONLY path to it is through
// Manager.validateRound (which checks the round before calling it). A cross-contract dependency clear
// here is path-dominant — the call graph shows no guard-free entry reaches `_apply`.
contract Vault {
    uint256 internal state;

    function _apply(uint256 v) internal {            // internal — not directly attacker-callable
        state = v;
    }

    // Exposed only via the guarded manager flow below.
    function applyVia(uint256 v) external onlyManager { _apply(v); }

    modifier onlyManager() { _; }
}

contract Manager {
    Vault vault;

    function validateRound(uint256 round, uint256 v) public {
        require(round == currentRound(), "stale round"); // the guard
        vault.applyVia(v);                                // only path to Vault._apply
    }

    function currentRound() public view returns (uint256) { return 1; }
}
