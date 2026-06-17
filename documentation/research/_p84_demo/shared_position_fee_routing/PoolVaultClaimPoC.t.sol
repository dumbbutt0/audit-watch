// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// SCAFFOLD — handoff generator, finding type: Shared-accounting / fee-routing (shared_position_fee_routing)
// Target: PoolVault.claim (EX-FEE-01)
//
// This is a NON-PASSING stub. It must be implemented from SOURCE BEHAVIOR (not an answer key) and must FAIL
// on the vulnerable source for the expected reason before it counts as a reproduction. The guard at the end
// of the test body guarantees it cannot report a false pass until you remove it after implementing L1–L3.
//
// Invariant to encode (this finding type):
//   order-independence / value-conservation: a user's claim proceeds must be independent of whether another sharer of the same pooled position acted first; total distributed must conserve each sharer's entitlement.
// Setup hint:
//   Set up >=2 users holding internal shares of ONE shared position; accrue fees via realistic trading; compare a user's payout claiming first vs claiming after another user using vm.snapshot/vm.revertTo at the same unlock and price.
//
// Level-3 PoC standard — all three layers must be proven:
//   L1 (Entry):     attacker/user tx crafted from an EOA with no privileged setup.
//   L2 (State flip): name the exact storage slots / balances and assert before/after (vm.load / balanceOf).
//   L3 (Outcome):    prove the final economic/security consequence in test output — do not infer it.

import "forge-std/Test.sol";
// TODO: import the in-scope contract(s) and the repo's own test harness/base if one exists.

contract PoolVaultClaimPoC is Test {
    function setUp() external {
        // TODO L1: deploy/initialize the in-scope contracts LOCALLY (fork mainnet only for stable deps).
        // Set up >=2 users holding internal shares of ONE shared position; accrue fees via realistic trading; compare a user's payout claiming first vs claiming after another user using vm.snapshot/vm.revertTo at the same unlock and price.
    }

    function test_EX_FEE_01_invariant() external {
        // TODO L1 — Entry: craft the unprivileged transaction(s) that reach claim.

        // TODO L2 — State flip: capture the named slots/balances before, perform the action, assert after.
        //   uint256 before = ...; <action>; uint256 afterV = ...;

        // TODO L3 — Outcome: assert the concrete consequence that breaks the invariant:
        //   order-independence / value-conservation: a user's claim proceeds must be independent of whether another sharer of the same pooled position acted first; total distributed must conserve each sharer's entitlement.
        //   (e.g. compare the harmed party's proceeds across two orderings via vm.snapshot/vm.revertTo,
        //    or assert the unauthorized call succeeded and guarded state changed,
        //    or assert the manipulated price changed the protocol's decision — per finding type.)

        // Reject-first guard: REMOVE only after L1–L3 are implemented and the assertions above carry the proof.
        assertTrue(false, "P84 SCAFFOLD: implement L1/L2/L3 and the invariant assertion before running");
    }

    // Negative control (run after a minimal patch to prove the root cause):
    //   Collect only the per-claim amounts the caller is owed (e.g. collect(uint128(amount0), uint128(amount1)) instead of collect(max, max)), or advance each internal share's fee checkpoint, so other users' fees stay in the position. Assert the later claim pays the same as the order-independent baseline and does not revert.
    // TODO: add a test asserting the invariant HOLDS under the minimal patch.
}
