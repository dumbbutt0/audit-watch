// SPDX-License-Identifier: MIT
// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement an
// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance candidate status.
// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.
pragma solidity ^0.8.0;

// import "forge-std/Test.sol";  // (uncomment in a Foundry project)
//   candidate: kleidi-2024-10 :: AddressCalculation.calculateAddressUnsafe
//   harness classification: HARNESS_MODERATE — 5 in-scope contract(s), local deploy with ordering / initialization
// TODO dep (in-scope): import "src/InstanceDeployer.sol";
// TODO dep (in-scope): import "src/Timelock.sol";
// TODO dep (in-scope): import "src/TimelockFactory.sol";
// TODO dep (in-scope): import "src/utils/Create2Helper.sol";

contract AddressCalculation_calculateAddressUnsafeHarnessScaffold /* is Test */ {

    // --- actors (who the runtime test needs) ---
    address attacker = makeAddr("attacker"); // EOA entrypoint (default adversary)
    address protocol = makeAddr("protocol"); // external protocol surface (factory/pair/pool/oracle)
    address governance = makeAddr("governance"); // governance/timelock present

    // --- contract handles under test ---
    AddressCalculation addressCalculation; // TODO: deploy in setUp
    Create2Helper create2Helper; // TODO: deploy in setUp
    InstanceDeployer instanceDeployer; // TODO: deploy in setUp
    Timelock timelock; // TODO: deploy in setUp
    TimelockFactory timelockFactory; // TODO: deploy in setUp

    function setUp() public {
        // TODO[deploy]: addressCalculation = new AddressCalculation(/* constructor args */);
        // TODO[deploy]: create2Helper = new Create2Helper(/* constructor args */);
        // TODO[deploy]: instanceDeployer = new InstanceDeployer(/* constructor args */);
        // TODO[deploy]: timelock = new Timelock(/* constructor args */);
        // TODO[deploy]: timelockFactory = new TimelockFactory(/* constructor args */);
    }

    function test_runtime_candidate() public {
        // TODO: build the runtime check for the candidate invariant on AddressCalculation.calculateAddressUnsafe.
        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.
        // A human completes this to either reproduce or refute the behavior at runtime.
        vm.skip(true); // inert: scaffold is not an executable adversarial sequence
    }
}
