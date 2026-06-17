// SPDX-License-Identifier: MIT
// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement an
// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance candidate status.
// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.
pragma solidity ^0.8.0;

// import "forge-std/Test.sol";  // (uncomment in a Foundry project)
//   candidate: iq-ai-2025-01 :: AgentRouter.sell
//   harness classification: HARNESS_COMPLEX — fork / external-state recreation required (1 hardcoded mainnet address(es); external protocol integration import(s): dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol, dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol)
// TODO dep (in-scope): import "./AgentFactory.sol";
// TODO dep (in-scope): import "./BootstrapPool.sol";
// TODO dep (in-scope): import "./LiquidityManager.sol";
// TODO dep (EXTERNAL — fork): dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol
// TODO dep (EXTERNAL — fork): dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol
// TODO dep (token): @openzeppelin/contracts/interfaces/IERC20.sol
// TODO dep (token): @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol

contract AgentRouter_sellHarnessScaffold /* is Test */ {

    // --- actors (who the runtime test needs) ---
    address attacker = makeAddr("attacker"); // EOA entrypoint (default adversary)
    address liquidity_provider = makeAddr("liquidity_provider"); // liquidity/reserve mechanics present
    address protocol = makeAddr("protocol"); // external protocol surface (factory/pair/pool/oracle)

    // --- contract handles under test ---
    AgentFactory agentFactory; // TODO: deploy in setUp
    AgentRouter agentRouter; // TODO: deploy in setUp
    BootstrapPool bootstrapPool; // TODO: deploy in setUp
    LiquidityManager liquidityManager; // TODO: deploy in setUp

    function setUp() public {
        // TODO[fork]: vm.createSelectFork(<RPC>, <block>); reasons: 1 hardcoded mainnet address(es); external protocol integration import(s): dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol, dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol
        // TODO[deploy]: agentFactory = new AgentFactory(/* constructor args */);
        // TODO[deploy]: agentRouter = new AgentRouter(/* constructor args */);
        // TODO[deploy]: bootstrapPool = new BootstrapPool(/* constructor args */);
        // TODO[deploy]: liquidityManager = new LiquidityManager(/* constructor args */);
        // TODO[fund]: mint/deal tokens to the actors that need balances
    }

    function test_runtime_candidate() public {
        // TODO: build the runtime check for the candidate invariant on AgentRouter.sell.
        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.
        // A human completes this to either reproduce or refute the behavior at runtime.
        vm.skip(true); // inert: scaffold is not an executable adversarial sequence
    }
}
