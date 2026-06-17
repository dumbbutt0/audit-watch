// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// SCAFFOLD — handoff generator, finding type: Reward-accrual / state-lifecycle (reward_accrual_state_lifecycle)
// Target: TraitForgeNft.mintWithBudget (P87-H01)
//
// This is a NON-PASSING stub. It must be implemented from SOURCE BEHAVIOR (not an answer key) and must FAIL
// on the vulnerable source for the expected reason before it counts as a reproduction. The guard at the end
// of the test body guarantees it cannot report a false pass until you remove it after implementing L1–L3.
//
// Invariant to encode (this finding type):
//   reward-lifecycle invariant: a validly-participating user must keep accruing; a dirty/stale flag or per-user reward checkpoint (reward debt / index) must be reset/advanced when the user returns to a valid state; reward owed must remain claimable. Set-but-never-reset breaks this permanently.
// Setup hint:
//   Put a user in a valid reward-earning state; trigger the path that sets the dirty/stale flag or skips the checkpoint update; restore the valid state (re-enter / move to a valid slot / re-lock); read the flag/checkpoint storage slot before/after to show it is NOT reset; then show the user accrues 0 / cannot claim owed reward and that no normal later action recovers it.
//
// Level-3 PoC standard — all three layers must be proven:
//   L1 (Entry):     attacker/user tx crafted from an EOA with no privileged setup.
//   L2 (State flip): name the exact storage slots / balances and assert before/after (vm.load / balanceOf).
//   L3 (Outcome):    prove the final economic/security consequence in test output — do not infer it.

import "forge-std/Test.sol";
// TODO: import the in-scope contract(s) and the repo's own test harness/base if one exists.

contract TraitForgeNftMintWithBudgetPoC is Test {
    function setUp() external {
        // TODO L1: deploy/initialize the in-scope contracts LOCALLY (fork mainnet only for stable deps).
        // Put a user in a valid reward-earning state; trigger the path that sets the dirty/stale flag or skips the checkpoint update; restore the valid state (re-enter / move to a valid slot / re-lock); read the flag/checkpoint storage slot before/after to show it is NOT reset; then show the user accrues 0 / cannot claim owed reward and that no normal later action recovers it.
    }

    function test_P87_H01_invariant() external {
        // TODO L1 — Entry: craft the unprivileged transaction(s) that reach mintWithBudget.

        // TODO L2 — State flip: capture the named slots/balances before, perform the action, assert after.
        //   uint256 before = ...; <action>; uint256 afterV = ...;

        // TODO L3 — Outcome: assert the concrete consequence that breaks the invariant:
        //   reward-lifecycle invariant: a validly-participating user must keep accruing; a dirty/stale flag or per-user reward checkpoint (reward debt / index) must be reset/advanced when the user returns to a valid state; reward owed must remain claimable. Set-but-never-reset breaks this permanently.
        //   (e.g. compare the harmed party's proceeds across two orderings via vm.snapshot/vm.revertTo,
        //    or assert the unauthorized call succeeded and guarded state changed,
        //    or assert the manipulated price changed the protocol's decision — per finding type.)

        // Reject-first guard: REMOVE only after L1–L3 are implemented and the assertions above carry the proof.
        assertTrue(false, "P84 SCAFFOLD: implement L1/L2/L3 and the invariant assertion before running");
    }

    // Negative control (run after a minimal patch to prove the root cause):
    //   Reset the dirty/stale flag to false (or advance the per-user reward checkpoint / clear the reward debt) on the recovery path (e.g. inside transferToUnoccupiedPlot / on re-entry), and set lastRewardDate to block.timestamp. Assert the participant resumes accruing the recoverable baseline and can claim owed reward, with no other change.
    // TODO: add a test asserting the invariant HOLDS under the minimal patch.
}
