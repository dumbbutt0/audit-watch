// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// Safe: clamp instead of underflow-revert, so a liquidatable account is never blocked by the "gate".
library BonusSafe {
    function compute(uint256 balanceCross, uint256 thresholdCross) internal pure returns (uint256) {
        if (thresholdCross <= balanceCross) return 0;                    // no liveness block
        return _min(balanceCross / 2, thresholdCross - balanceCross);
    }
    function _min(uint256 a, uint256 b) private pure returns (uint256) { return a < b ? a : b; }
}
