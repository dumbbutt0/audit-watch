// SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

// SCAFFOLD — handoff generator, finding type: Access-control / privileged (missing_auth_accounting_drift)
// Target: Cred._addCredIdPerAddress (P89-H05)
//
// This is a NON-PASSING stub. It must be implemented from SOURCE BEHAVIOR (not an answer key) and must FAIL
// on the vulnerable source for the expected reason before it counts as a reproduction. The guard at the end
// of the test body guarantees it cannot report a false pass until you remove it after implementing L1–L3.
//
// Invariant to encode (this finding type):
//   authorization invariant: a state-mutating or value-moving function must reject callers without the required role; an unauthorized EOA/contract call must revert (and leave guarded state unchanged).
// Setup hint:
//   From an unprivileged attacker account/contract, call the under-guarded entrypoint directly; assert the call succeeds when it should not, the guarded state mutated, and (for High) a downstream fund-impacting consequence follows.
//
// Level-3 PoC standard — all three layers must be proven:
//   L1 (Entry):     attacker/user tx crafted from an EOA with no privileged setup.
//   L2 (State flip): name the exact storage slots / balances and assert before/after (vm.load / balanceOf).
//   L3 (Outcome):    prove the final economic/security consequence in test output — do not infer it.

import "forge-std/Test.sol";
// TODO: import the in-scope contract(s) and the repo's own test harness/base if one exists.

contract CredAddCredIdPerAddressPoC is Test {
    function setUp() external {
        // TODO L1: deploy/initialize the in-scope contracts LOCALLY (fork mainnet only for stable deps).
        // From an unprivileged attacker account/contract, call the under-guarded entrypoint directly; assert the call succeeds when it should not, the guarded state mutated, and (for High) a downstream fund-impacting consequence follows.
    }

    function test_P89_H05_invariant() external {
        // TODO L1 — Entry: craft the unprivileged transaction(s) that reach _addCredIdPerAddress.

        // TODO L2 — State flip: capture the named slots/balances before, perform the action, assert after.
        //   uint256 before = ...; <action>; uint256 afterV = ...;

        // TODO L3 — Outcome: assert the concrete consequence that breaks the invariant:
        //   authorization invariant: a state-mutating or value-moving function must reject callers without the required role; an unauthorized EOA/contract call must revert (and leave guarded state unchanged).
        //   (e.g. compare the harmed party's proceeds across two orderings via vm.snapshot/vm.revertTo,
        //    or assert the unauthorized call succeeded and guarded state changed,
        //    or assert the manipulated price changed the protocol's decision — per finding type.)

        // Reject-first guard: REMOVE only after L1–L3 are implemented and the assertions above carry the proof.
        assertTrue(false, "P84 SCAFFOLD: implement L1/L2/L3 and the invariant assertion before running");
    }

    // Negative control (run after a minimal patch to prove the root cause):
    //   Add onlyRegistratorOrGovernor modifier. Assert that the attacker contract call reverts. Assert totalDepositsWei unchanged.
    // TODO: add a test asserting the invariant HOLDS under the minimal patch.
}
