# P110 — Harness scaffold examples

Inert Foundry skeletons (banner + actors + handles + setUp TODOs + `vm.skip(true)` test stub). Each passes `assert_scaffold_is_inert` — no exploit logic, no consequence assertion, no conclusion.

## Positive controls

### iq-ai-2025-01 :: moveLiquidity (HARNESS_COMPLEX)
overlap vs real harness: {'harness_present': True, 'real_fork': True, 'scaffold_fork': True, 'fork_match': True, 'real_deployed': ['AgentFactory'], 'scaffold_dep_hits': ['AgentFactory'], 'dep_overlap': 1.0, 'real_actor_count': 2, 'scaffold_actor_count': 4, 'scaffold_is_inert': True}

```solidity
// SPDX-License-Identifier: MIT
// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement an
// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance candidate status.
// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.
pragma solidity ^0.8.0;

// import "forge-std/Test.sol";  // (uncomment in a Foundry project)
//   candidate: iq-ai-2025-01 :: LiquidityManager.moveLiquidity
//   harness classification: HARNESS_COMPLEX — fork / external-state recreation required (2 hardcoded mainnet address(es); external protocol integration import(s): dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol, dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol, dev-fraxswap/src/contracts/core/libraries/Math.sol)
// TODO dep (in-scope): import "./AgentFactory.sol";
// TODO dep (in-scope): import "./BootstrapPool.sol";
// TODO dep (in-scope): import "./interface/IBAMM.sol";
// TODO dep (in-scope): import "./interface/IBAMMFactory.sol";
// TODO dep (EXTERNAL — fork): dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol
// TODO dep (EXTERNAL — fork): dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol
// TODO dep (EXTERNAL — fork): dev-fraxswap/src/contracts/core/libraries/Math.sol
// TODO dep (token): @openzeppelin/contracts/interfaces/IERC20.sol
// TODO dep (token): @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol

contract LiquidityManager_moveLiquidityHarnessScaffold /* is Test */ {

    // --- actors (who the runtime test needs) ---
    address attacker = makeAddr("attacker"); // EOA entrypoint (default adversary)
    address victim_user = makeAddr("victim_user"); // per-user accounting present
    address liquidity_provider = makeAddr("liquidity_provider"); // liquidity/reserve mechanics present
    address protocol = makeAddr("protocol"); // external protocol surface (factory/pair/pool/oracle)

    // --- contract handles under test ---
    AgentFactory agentFactory; // TODO: deploy in setUp
    BootstrapPool bootstrapPool; // TODO: deploy in setUp
    LiquidityManager liquidityManager; // TODO: deploy in setUp

    function setUp() public {
        // TODO[fork]: vm.createSelectFork(<RPC>, <block>); reasons: 2 hardcoded mainnet address(es); external protocol integration import(s): dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol, dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol, dev-fraxswap/src/contracts/core/libraries/Math.sol
        // TODO[deploy]: agentFactory = new AgentFactory(/* constructor args */);
        // TODO[deploy]: bootstrapPool = new BootstrapPool(/* constructor args */);
        // TODO[deploy]: liquidityManager = new LiquidityManager(/* constructor args */);
        // TODO[fund]: mint/deal tokens to the actors that need balances
    }

    function test_runtime_candidate() public {
        // TODO: build the runtime check for the candidate invariant on LiquidityManager.moveLiquidity.
        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.
        // A human completes this to either reproduce or refute the behavior at runtime.
        vm.skip(true); // inert: scaffold is not an executable adversarial sequence
    }
}

```

### secondswap-2024-12 :: spotPurchase (HARNESS_MODERATE)
overlap vs real harness: {'harness_present': True, 'real_fork': False, 'scaffold_fork': False, 'fork_match': True, 'real_deployed': ['MockERC20', 'SecondSwap_Marketplace', 'SecondSwap_MarketplaceSetting', 'SecondSwap_StepVesting', 'SecondSwap_VestingManager'], 'scaffold_dep_hits': ['SecondSwap_Marketplace', 'SecondSwap_MarketplaceSetting', 'SecondSwap_VestingManager'], 'dep_overlap': 0.6, 'real_actor_count': 6, 'scaffold_actor_count': 3, 'scaffold_is_inert': True}

```solidity
// SPDX-License-Identifier: MIT
// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement an
// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance candidate status.
// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.
pragma solidity ^0.8.0;

// import "forge-std/Test.sol";  // (uncomment in a Foundry project)
//   candidate: secondswap-2024-12 :: SecondSwap_Marketplace.spotPurchase
//   harness classification: HARNESS_MODERATE — 6 in-scope contract(s), local deploy with ordering / initialization
// TODO dep (in-scope): import "./SecondSwap_WhitelistDeployer.sol";
// TODO dep (in-scope): import "./interface/IERC20.sol";
// TODO dep (in-scope): import "./interface/SecondSwap_IMarketplaceSetting.sol";
// TODO dep (in-scope): import "./interface/SecondSwap_IVestingManager.sol";
// TODO dep (in-scope): import "./interface/SecondSwap_IWhitelist.sol";
// TODO dep (token): ./interface/IERC20.sol
// TODO dep (token): @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol

contract SecondSwap_Marketplace_spotPurchaseHarnessScaffold /* is Test */ {

    // --- actors (who the runtime test needs) ---
    address attacker = makeAddr("attacker"); // EOA entrypoint (default adversary)
    address admin = makeAddr("admin"); // owner/role/privileged guard present
    address victim_user = makeAddr("victim_user"); // per-user accounting present

    // --- contract handles under test ---
    ERC20 eRC20; // TODO: deploy in setUp
    SecondSwap_Marketplace secondSwap_Marketplace; // TODO: deploy in setUp
    SecondSwap_MarketplaceSetting secondSwap_MarketplaceSetting; // TODO: deploy in setUp
    SecondSwap_VestingManager secondSwap_VestingManager; // TODO: deploy in setUp
    SecondSwap_Whitelist secondSwap_Whitelist; // TODO: deploy in setUp
    SecondSwap_WhitelistDeployer secondSwap_WhitelistDeployer; // TODO: deploy in setUp

    function setUp() public {
        // TODO[deploy]: eRC20 = new ERC20(/* constructor args */);
        // TODO[deploy]: secondSwap_Marketplace = new SecondSwap_Marketplace(/* constructor args */);
        // TODO[deploy]: secondSwap_MarketplaceSetting = new SecondSwap_MarketplaceSetting(/* constructor args */);
        // TODO[deploy]: secondSwap_VestingManager = new SecondSwap_VestingManager(/* constructor args */);
        // TODO[deploy]: secondSwap_Whitelist = new SecondSwap_Whitelist(/* constructor args */);
        // TODO[deploy]: secondSwap_WhitelistDeployer = new SecondSwap_WhitelistDeployer(/* constructor args */);
        // TODO[config]: call initialize(...) / setter(s) to reach a valid pre-state
        // TODO[fund]: mint/deal tokens to the actors that need balances
    }

    function test_runtime_candidate() public {
        // TODO: build the runtime check for the candidate invariant on SecondSwap_Marketplace.spotPurchase.
        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.
        // A human completes this to either reproduce or refute the behavior at runtime.
        vm.skip(true); // inert: scaffold is not an executable adversarial sequence
    }
}

```

## One representative per classification

### vultisig-2024-06 :: ILOManager.initialize (HARNESS_COMPLEX)

```solidity
// SPDX-License-Identifier: MIT
// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement an
// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance candidate status.
// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.
pragma solidity ^0.8.0;

// import "forge-std/Test.sol";  // (uncomment in a Foundry project)
//   candidate: vultisig-2024-06 :: ILOManager.initialize
//   harness classification: HARNESS_COMPLEX — fork / external-state recreation required (external protocol integration import(s): @uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol, @uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol, @uniswap/v3-core/contracts/libraries/TickMath.sol)
// TODO dep (in-scope): import "./base/Initializable.sol";
// TODO dep (in-scope): import "./interfaces/IILOManager.sol";
// TODO dep (in-scope): import "./interfaces/IILOPool.sol";
// TODO dep (in-scope): import "./libraries/ChainId.sol";
// TODO dep (EXTERNAL — fork): @uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol
// TODO dep (EXTERNAL — fork): @uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol
// TODO dep (EXTERNAL — fork): @uniswap/v3-core/contracts/libraries/TickMath.sol

contract ILOManager_initializeHarnessScaffold /* is Test */ {

    // --- actors (who the runtime test needs) ---
    address attacker = makeAddr("attacker"); // EOA entrypoint (default adversary)
    address admin = makeAddr("admin"); // owner/role/privileged guard present
    address victim_user = makeAddr("victim_user"); // per-user accounting present
    address liquidity_provider = makeAddr("liquidity_provider"); // liquidity/reserve mechanics present
    address protocol = makeAddr("protocol"); // external protocol surface (factory/pair/pool/oracle)

    // --- contract handles under test ---
    ChainId chainId; // TODO: deploy in setUp
    ILOManager iLOManager; // TODO: deploy in setUp
    ILOPool iLOPool; // TODO: deploy in setUp
    Initializable initializable; // TODO: deploy in setUp

    function setUp() public {
        // TODO[fork]: vm.createSelectFork(<RPC>, <block>); reasons: external protocol integration import(s): @uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol, @uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol, @uniswap/v3-core/contracts/libraries/TickMath.sol
        // TODO[deploy]: chainId = new ChainId(/* constructor args */);
        // TODO[deploy]: iLOManager = new ILOManager(/* constructor args */);
        // TODO[deploy]: iLOPool = new ILOPool(/* constructor args */);
        // TODO[deploy]: initializable = new Initializable(/* constructor args */);
        // TODO[config]: call initialize(...) / setter(s) to reach a valid pre-state
        // TODO[fund]: mint/deal tokens to the actors that need balances
    }

    function test_runtime_candidate() public {
        // TODO: build the runtime check for the candidate invariant on ILOManager.initialize.
        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.
        // A human completes this to either reproduce or refute the behavior at runtime.
        vm.skip(true); // inert: scaffold is not an executable adversarial sequence
    }
}

```

### vultisig-2024-06 :: Multicall.multicall (HARNESS_SIMPLE)

```solidity
// SPDX-License-Identifier: MIT
// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement an
// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance candidate status.
// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.
pragma solidity ^0.8.0;

// import "forge-std/Test.sol";  // (uncomment in a Foundry project)
//   candidate: vultisig-2024-06 :: Multicall.multicall
//   harness classification: HARNESS_SIMPLE — isolated contract, local deployment sufficient, minimal actors
// TODO dep (in-scope): import "../interfaces/IMulticall.sol";

contract Multicall_multicallHarnessScaffold /* is Test */ {

    // --- actors (who the runtime test needs) ---
    address attacker = makeAddr("attacker"); // EOA entrypoint (default adversary)

    // --- contract handles under test ---
    Multicall multicall; // TODO: deploy in setUp

    function setUp() public {
        // TODO[deploy]: multicall = new Multicall(/* constructor args */);
    }

    function test_runtime_candidate() public {
        // TODO: build the runtime check for the candidate invariant on Multicall.multicall.
        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.
        // A human completes this to either reproduce or refute the behavior at runtime.
        vm.skip(true); // inert: scaffold is not an executable adversarial sequence
    }
}

```

### phi-2024-08 :: PhiNFT1155.claimFromFactory (HARNESS_MODERATE)

```solidity
// SPDX-License-Identifier: MIT
// SCAFFOLD ONLY — P110 harness preparation. This prepares a runtime environment; it does NOT implement an
// adversarial sequence, does NOT establish a finding, assigns no rating, and does not advance candidate status.
// The test body is inert (vm.skip). Fill the TODOs to build a runtime check.
pragma solidity ^0.8.0;

// import "forge-std/Test.sol";  // (uncomment in a Foundry project)
//   candidate: phi-2024-08 :: PhiNFT1155.claimFromFactory
//   harness classification: HARNESS_MODERATE — 5 in-scope contract(s), local deploy with ordering / initialization
// TODO dep (in-scope): import "../abstract/Claimable.sol";
// TODO dep (in-scope): import "../abstract/CreatorRoyaltiesControl.sol";
// TODO dep (in-scope): import "../interfaces/IPhiFactory.sol";
// TODO dep (in-scope): import "../interfaces/IPhiNFT1155.sol";
// TODO dep (in-scope): import "../interfaces/IPhiRewards.sol";
// TODO dep (token): @openzeppelin/contracts-upgradeable/token/ERC1155/ERC1155Upgradeable.sol
// TODO dep (token): @openzeppelin/contracts-upgradeable/token/ERC1155/extensions/ERC1155SupplyUpgradeable.sol

contract PhiNFT1155_claimFromFactoryHarnessScaffold /* is Test */ {

    // --- actors (who the runtime test needs) ---
    address attacker = makeAddr("attacker"); // EOA entrypoint (default adversary)
    address admin = makeAddr("admin"); // owner/role/privileged guard present
    address protocol = makeAddr("protocol"); // external protocol surface (factory/pair/pool/oracle)

    // --- contract handles under test ---
    Claimable claimable; // TODO: deploy in setUp
    CreatorRoyaltiesControl creatorRoyaltiesControl; // TODO: deploy in setUp
    PhiFactory phiFactory; // TODO: deploy in setUp
    PhiNFT1155 phiNFT1155; // TODO: deploy in setUp
    PhiRewards phiRewards; // TODO: deploy in setUp

    function setUp() public {
        // TODO[deploy]: claimable = new Claimable(/* constructor args */);
        // TODO[deploy]: creatorRoyaltiesControl = new CreatorRoyaltiesControl(/* constructor args */);
        // TODO[deploy]: phiFactory = new PhiFactory(/* constructor args */);
        // TODO[deploy]: phiNFT1155 = new PhiNFT1155(/* constructor args */);
        // TODO[deploy]: phiRewards = new PhiRewards(/* constructor args */);
        // TODO[config]: call initialize(...) / setter(s) to reach a valid pre-state
        // TODO[fund]: mint/deal tokens to the actors that need balances
    }

    function test_runtime_candidate() public {
        // TODO: build the runtime check for the candidate invariant on PhiNFT1155.claimFromFactory.
        // SCAFFOLD ONLY — do NOT implement an adversarial sequence or a consequence check here.
        // A human completes this to either reproduce or refute the behavior at runtime.
        vm.skip(true); // inert: scaffold is not an executable adversarial sequence
    }
}

```

