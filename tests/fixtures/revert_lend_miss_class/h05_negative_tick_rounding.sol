// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// H-05: tickCumulative delta is divided without rounding DOWN for negative deltas → the derived TWAP tick
// is rounded toward zero, inflating the reference pool price.
library Oracle {
    function twapTick(int56 delta, uint32 period) internal pure returns (int24) {
        int24 t = int24(delta / int56(uint56(period)));       // BUG: truncates toward zero for negative
        return t;
    }
}
