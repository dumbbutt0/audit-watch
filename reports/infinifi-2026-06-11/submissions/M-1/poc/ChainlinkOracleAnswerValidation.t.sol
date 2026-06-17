// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Test, console2} from "forge-std/Test.sol";
import {ChainlinkOracle} from "../src/finance/oracles/ChainlinkOracle.sol";

/// @notice Mock Chainlink aggregator with a configurable answer and fresh updatedAt.
contract MockAggregator {
    int256 public answer;
    constructor(int256 _answer) { answer = _answer; }
    function setAnswer(int256 a) external { answer = a; }
    function latestRoundData()
        external
        view
        returns (uint80, int256, uint256, uint256, uint80)
    {
        return (1, answer, block.timestamp, block.timestamp, 1); // updatedAt = now (never stale)
    }
}

/// @notice PoC: ChainlinkOracle.price() lacks an `answer > 0` check, so a non-positive Chainlink
///         answer is consumed as-is — yielding a $0 price (under-valuation) or, for a negative
///         answer, an astronomically large price (over-valuation) via the unchecked int256->uint256 cast.
contract ChainlinkOracleAnswerValidationTest is Test {
    function setUp() public {
        vm.warp(1_000_000);
    }

    /// answer == 0 (e.g. faulty round / feed not yet initialized) -> price() returns 0.
    /// In Accounting.totalAssetsValue() the asset is then valued at $0.
    function test_zeroAnswer_pricesAssetAtZero() public {
        MockAggregator feed = new MockAggregator(0);
        // 8-decimal feed normalized up to 18 decimals: decimalNormalization=1e10, divide=false
        ChainlinkOracle oracle = new ChainlinkOracle(address(feed), 1e10, false, 1 days);
        uint256 p = oracle.price();
        console2.log("price() with answer==0:", p);
        assertEq(p, 0, "zero answer accepted, asset valued at $0 (undervaluation -> unjust slash / redeem DoS)");
    }

    /// answer < 0 -> uint256(answer) is ~2^256, an astronomically large price (over-valuation).
    /// Using divide-mode so the multiply path doesn't overflow-revert; result is still catastrophic.
    function test_negativeAnswer_pricesAssetAstronomically() public {
        MockAggregator feed = new MockAggregator(-1);
        ChainlinkOracle oracle = new ChainlinkOracle(address(feed), 1e8, true, 1 days); // divide=true
        uint256 p = oracle.price();
        console2.log("price() with answer==-1 (divide mode):", p);
        // uint256(-1) / 1e8  ~= 1.15e69 -> the asset is overvalued by ~1e69x
        assertGt(p, 1e60, "negative answer -> astronomically large price (overvaluation -> phantom iUSD mint)");
    }

    /// Control: the SAME oracle correctly handles a normal positive answer, proving the only gap is validation.
    function test_positiveAnswer_ok() public {
        MockAggregator feed = new MockAggregator(1e8); // $1.00 at 8 decimals
        ChainlinkOracle oracle = new ChainlinkOracle(address(feed), 1e10, false, 1 days);
        assertEq(oracle.price(), 1e18, "normal $1 feed -> 1e18 (18-dec normalized)");
    }
}
