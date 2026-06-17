// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// VULNERABLE: fee should INCREASE with risk, but the code subtracts risk so the fee FALLS as risk rises
// (and underflows past base). The economic-direction check (monotonicity_and_economic_direction) catches
// this; the formula-diff harness reports a monotonicity inversion vs intended `base + risk * k`.
contract FeeMonotonicity {
    uint256 public base;

    function feeFor(uint256 risk, uint256 k) public view returns (uint256) {
        for (uint256 i = 0; i < 1; i++) {}          // structural signal for the math lens
        return base - risk * k;                      // wrong direction: fee decreases with risk
    }
}
