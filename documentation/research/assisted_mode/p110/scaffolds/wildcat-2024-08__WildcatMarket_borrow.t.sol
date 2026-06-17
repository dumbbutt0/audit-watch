// SPDX-License-Identifier: MIT
// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement an
// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance candidate status.
// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.
pragma solidity ^0.8.0;

// import "forge-std/Test.sol";  // (uncomment in a Foundry project)
//   candidate: wildcat-2024-08 :: WildcatMarket.borrow
//   harness classification: HARNESS_MODERATE — 6 in-scope contract(s), local deploy with ordering / initialization
// TODO dep (in-scope): import "../WildcatSanctionsSentinel.sol";
// TODO dep (in-scope): import "./WildcatMarketBase.sol";
// TODO dep (in-scope): import "./WildcatMarketConfig.sol";
// TODO dep (in-scope): import "./WildcatMarketToken.sol";
// TODO dep (in-scope): import "./WildcatMarketWithdrawals.sol";

contract WildcatMarket_borrowHarnessScaffold /* is Test */ {

    // --- actors (who the runtime test needs) ---
    address attacker = makeAddr("attacker"); // EOA entrypoint (default adversary)
    address victim_user = makeAddr("victim_user"); // per-user accounting present
    address liquidity_provider = makeAddr("liquidity_provider"); // liquidity/reserve mechanics present

    // --- contract handles under test ---
    WildcatMarket wildcatMarket; // TODO: deploy in setUp
    WildcatMarketBase wildcatMarketBase; // TODO: deploy in setUp
    WildcatMarketConfig wildcatMarketConfig; // TODO: deploy in setUp
    WildcatMarketToken wildcatMarketToken; // TODO: deploy in setUp
    WildcatMarketWithdrawals wildcatMarketWithdrawals; // TODO: deploy in setUp
    WildcatSanctionsSentinel wildcatSanctionsSentinel; // TODO: deploy in setUp

    function setUp() public {
        // TODO[deploy]: wildcatMarket = new WildcatMarket(/* constructor args */);
        // TODO[deploy]: wildcatMarketBase = new WildcatMarketBase(/* constructor args */);
        // TODO[deploy]: wildcatMarketConfig = new WildcatMarketConfig(/* constructor args */);
        // TODO[deploy]: wildcatMarketToken = new WildcatMarketToken(/* constructor args */);
        // TODO[deploy]: wildcatMarketWithdrawals = new WildcatMarketWithdrawals(/* constructor args */);
        // TODO[deploy]: wildcatSanctionsSentinel = new WildcatSanctionsSentinel(/* constructor args */);
        // TODO[fund]: mint/deal tokens to the actors that need balances
    }

    function test_runtime_candidate() public {
        // TODO: build the runtime check for the candidate invariant on WildcatMarket.borrow.
        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.
        // A human completes this to either reproduce or refute the behavior at runtime.
        vm.skip(true); // inert: scaffold is not an executable adversarial sequence
    }
}
