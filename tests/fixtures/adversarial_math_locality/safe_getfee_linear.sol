// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// SAFE: linear scaling, matching the intended model. A valid math_estimator_proof would state
// intended_formula = "2 * difficulty" (from the spec), implemented_formula = "2 * difficulty",
// monotonicity = "fee rises linearly with difficulty", and an attacker_favorable_search over the
// difficulty domain confirming no overflow within bounds.
contract FeeLinear {
    uint256 public platformFee;

    function getFee(uint256 difficulty, uint256 numGenerations) public view returns (uint256 total) {
        uint256 diff = 2 * difficulty;               // linear — matches intent
        for (uint256 i = 0; i < numGenerations; i++) {
            total += platformFee + diff;
        }
    }
}
