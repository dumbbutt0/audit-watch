// SPDX-License-Identifier: ISC
pragma solidity >=0.8.25 <0.9.0;

import {Test} from "forge-std/src/Test.sol";
import {AgentFactory} from "../../src/AgentFactory.sol";
import {TokenGovernor} from "../../src/TokenGovernor.sol";
import {Agent} from "../../src/Agent.sol";
import {AIToken} from "../../src/AIToken.sol";
import {LiquidityManager} from "../../src/LiquidityManager.sol";
import {BootstrapPool} from "../../src/BootstrapPool.sol";
import {IERC20} from "@openzeppelin/contracts/interfaces/IERC20.sol";

/// @notice P104 regression: with the minimal M-01 guard, an attacker-pre-created low-fee pair makes the
/// permissionless migration REVERT (the protocol no longer adopts the wrong-fee pair). Only meaningful with the
/// guard applied to LiquidityManager.addLiquidityToFraxswap.
contract M01PatchRegression is Test {
    IERC20 currencyToken = IERC20(0xFc00000000000000000000000000000000000001);
    address whale = 0x00160baF84b3D2014837cc12e838ea399f8b8478;
    address attacker = address(0xA11CE);
    AgentFactory factory; Agent agent; AIToken token; LiquidityManager manager; BootstrapPool bootstrapPool;

    function setUp() public { vm.createSelectFork(vm.envString("FRAXTAL_MAINNET_URL"), 12_918_968); }

    function _deploy() internal {
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
        for (uint256 i = 0; i < 100; i++) { (uint256 r,) = bootstrapPool.getReserves(); if (r - bootstrapPool.phantomAmount() > 1000e18) break; bootstrapPool.buy(10_000e18); }
        vm.stopPrank();
    }

    function test_patch_blocks_attacker_low_fee_pair() public {
        _deploy();
        vm.prank(attacker);
        manager.fraxswapFactory().createPair(address(currencyToken), address(token), 1); // low fee
        vm.prank(attacker);
        vm.expectRevert(bytes("M01: unexpected pre-existing pair fee"));
        manager.moveLiquidity();
    }

    function test_patch_allows_clean_migration() public {
        _deploy();
        vm.prank(attacker);
        manager.moveLiquidity(); // no pre-existing pair -> protocol creates it with intended fee -> succeeds
        assertTrue(manager.fraxswapFactory().getPair(address(currencyToken), address(token)) != address(0), "clean migration created the pair");
    }
}
