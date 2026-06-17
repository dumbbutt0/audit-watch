// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
library OracleSafe {
    function twapTick(int56 delta, uint32 period) internal pure returns (int24) {
        int24 t = int24(delta / int56(uint56(period)));
        if (delta < 0 && (delta % int56(uint56(period)) != 0)) t--;  // round DOWN for negative deltas
        return t;
    }
}
