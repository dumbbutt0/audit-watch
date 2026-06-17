// SPDX-License-Identifier: MIT
// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement an
// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance candidate status.
// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.
pragma solidity ^0.8.0;

// import "forge-std/Test.sol";  // (uncomment in a Foundry project)
//   candidate: phi-2024-08 :: Claimable.signatureClaim
//   harness classification: HARNESS_MODERATE — 2 in-scope contract(s), local deploy with ordering / initialization
// TODO dep (in-scope): import "../interfaces/IPhiFactory.sol";

contract Claimable_signatureClaimHarnessScaffold /* is Test */ {

    // --- actors (who the runtime test needs) ---
    address attacker = makeAddr("attacker"); // EOA entrypoint (default adversary)
    address protocol = makeAddr("protocol"); // external protocol surface (factory/pair/pool/oracle)

    // --- contract handles under test ---
    Claimable claimable; // TODO: deploy in setUp
    PhiFactory phiFactory; // TODO: deploy in setUp

    function setUp() public {
        // TODO[deploy]: claimable = new Claimable(/* constructor args */);
        // TODO[deploy]: phiFactory = new PhiFactory(/* constructor args */);
    }

    function test_runtime_candidate() public {
        // TODO: build the runtime check for the candidate invariant on Claimable.signatureClaim.
        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.
        // A human completes this to either reproduce or refute the behavior at runtime.
        vm.skip(true); // inert: scaffold is not an executable adversarial sequence
    }
}
