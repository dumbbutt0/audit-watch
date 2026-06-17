// SPDX-License-Identifier: MIT
// Fixture for the arithmetic_conservation lens. Distinct contract/fn names per scenario.
pragma solidity ^0.8.0;

// --- Scenario A: shape 1 positive (Blackhole M-01) — balanceOf read + multi-term supply aggregate -> HIGH
contract MinterLike {
    function calcRebase(uint _weeklyMint) public view returns (uint) {
        uint _veTotal = black.balanceOf(address(ve));
        uint _smNFTBalance = ve.smNFTBalance();
        uint _bonus = ve.bonus(_smNFTBalance);
        uint veBlackSupply = _veTotal + _smNFTBalance + _bonus;     // >=2 terms, name 'Supply' -> high
        uint blackSupply = black.totalSupply() + _bonus;
        uint circulatingBlack = blackSupply - veBlackSupply;
        return circulatingBlack;
    }
}

// --- Scenario B: shape 2 positive (Blackhole M-06) — product/curve invariant `_k` with integer division -> MEDIUM
contract PairLike {
    function _k(uint x, uint y) internal view returns (uint) {
        uint _x = x * 1e18 / decimals0;
        uint _y = y * 1e18 / decimals1;
        uint _a = (_x * _y) / 1e18;
        uint _b = ((_x * _x) / 1e18 + (_y * _y) / 1e18);
        return _a * _b / 1e18;
    }
}

// --- Scenario C: accumulator negative — `x = x + a` is accumulation, not a conservation aggregate
contract Accum {
    uint total;
    function add(uint a, uint b) public {
        total = total + a;
        reserve = reserve + b;
    }
}

// --- Scenario D: pure getter negative — no arithmetic
contract Getter {
    address _voter;
    function voter() external view returns (address) {
        return _voter;
    }
}

// --- Scenario E: plain swap negative — multi-term aggregate but NO balanceOf/totalSupply and no supply name
contract Swap {
    function quote(uint amountIn, uint reserveIn) internal pure returns (uint) {
        uint amtA = amountIn - reserveIn;
        uint fee = amountIn - amtA;
        return amtA - fee;
    }
}

// --- Scenario F: generic product/division negative — NOT a name-anchored invariant helper (shape 2 excludes)
contract Pricing {
    function getPrice(uint a, uint b, uint c) public pure returns (uint) {
        return a * b / c;
    }
}
