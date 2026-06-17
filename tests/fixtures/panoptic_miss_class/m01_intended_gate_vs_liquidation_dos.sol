// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// M-01 shape: `threshold - balance` is unsigned. For a distribution-insolvent account where balance >
// threshold in the cross terms, this underflows and REVERTS — framed as "solvent accounts can't be
// liquidated, intended gate", but it also blocks liquidating a genuinely insolvent (liquidatable) account.
library Bonus {
    function compute(uint256 balanceCross, uint256 thresholdCross) internal pure returns (uint256) {
        return _min(balanceCross / 2, thresholdCross - balanceCross);    // underflow → revert (DoS)
    }
    function _min(uint256 a, uint256 b) private pure returns (uint256) { return a < b ? a : b; }
}
