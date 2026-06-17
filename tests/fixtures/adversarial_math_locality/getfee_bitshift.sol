// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// VULNERABLE: the per-generation fee is meant to scale LINEARLY with difficulty (intended: 2*difficulty),
// but the code shifts (2 << difficulty == 2 * 2**difficulty) — exponential. A confirmatory proof that
// re-derives "diff = 2 << difficulty" from the code and calls it intended never questions the direction.
// This is the Swan/Dria M-08 getFee miss.
contract FeeExponential {
    uint256 public platformFee;

    function getFee(uint256 difficulty, uint256 numGenerations) public view returns (uint256 total) {
        uint256 diff = 2 << difficulty;              // exponential — should be linear
        for (uint256 i = 0; i < numGenerations; i++) {
            total += platformFee + diff;
        }
    }
}
