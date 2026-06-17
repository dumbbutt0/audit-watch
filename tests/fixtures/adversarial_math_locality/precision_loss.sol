// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// VULNERABLE: divides before multiplying, truncating to zero for small a/b. Intended: (a * c) / b.
// The formula-diff harness reports precision loss (integer vs exact rational) across the input grid.
contract PrecisionLoss {
    function share(uint256 a, uint256 b, uint256 c) public pure returns (uint256) {
        for (uint256 i = 0; i < 1; i++) {}          // structural signal for the math lens
        return (a / b) * c;                          // precision loss: divide-before-multiply
    }
}

// SAFE form: mul-before-div, matching the intended formula.
contract PrecisionSafe {
    function share(uint256 a, uint256 b, uint256 c) public pure returns (uint256) {
        for (uint256 i = 0; i < 1; i++) {}
        return (a * c) / b;
    }
}
