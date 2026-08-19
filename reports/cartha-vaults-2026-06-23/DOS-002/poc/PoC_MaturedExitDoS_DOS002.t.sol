// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console2} from "forge-std/Test.sol";
import {ERC1967Proxy} from "openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {UpgradeableBeacon} from "openzeppelin-contracts/contracts/proxy/beacon/UpgradeableBeacon.sol";
import {IERC20} from "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import {CarthaVaultFactory} from "../../src/CarthaVaultFactory.sol";
import {CarthaVault} from "../../src/CarthaVault.sol";
import {CarthaParentVault} from "../../src/CarthaParentVault.sol";
import {Diamond} from "../../src/diamond/Diamond.sol";
import {MockERC20} from "../mocks/MockERC20.sol";
import {MockExchangeRouter} from "../mocks/MockExchangeRouter.sol";
import {Mock0xMReader} from "../mocks/Mock0xMReader.sol";
import {Mock0xMOracle} from "../mocks/Mock0xMOracle.sol";
import {I0xMReader} from "../../src/interfaces/I0xMReader.sol";
import {DiamondTestUtils} from "../utils/DiamondTestUtils.sol";
import {ICarthaVaultFactory} from "../../src/interfaces/ICarthaVaultFactory.sol";
import {ICarthaVault} from "../../src/interfaces/ICarthaVault.sol";
import {ICarthaParentVault} from "../../src/interfaces/ICarthaParentVault.sol";
import {ICarthaAccessControl} from "../../src/interfaces/ICarthaAccessControl.sol";
import {Roles} from "../../src/diamond/Roles.sol";

/**
 * @title PoC — DOS-002 : a MATURED parent LP cannot exit while child funds are GM-deployed
 *
 * @notice Parent exits route through _prepareSharePayout (CarthaParentVault.sol:456-470): it can only
 *         satisfy a payout from parent idle USDC + `_availableFromChildren()`. But
 *         `_availableFromChildren()` (431-442) counts ONLY each child's IDLE USDC balance
 *         (`balanceOf(asset, vault)`) — it does NOT count the child's GM-deployed value. So once the
 *         KEEPER_BOT has deployed child USDC into the 0xM pool (deployToPool), a parent LP whose lock
 *         AND cooldown have BOTH expired still cannot withdraw: releaseFromParent reverts
 *         InsufficientVaultBalance (647), and the keeper batch path processQueuedParentWithdrawals
 *         silently `continue`s (699) with no payout. There is no permissionless force-recall and no
 *         emergency exit — deployToPool/recallFromPool are KEEPER_BOT-only — so a matured user's funds
 *         are reachable only if a trusted keeper first recalls the GM (async, multi-tx, 0xM-dependent).
 *         The value is fully present in totalAssets(); it is simply not withdrawable. Liveness /
 *         censorship risk: a stalled, offline, or adversarial keeper indefinitely blocks matured exits.
 */
contract PoC_MaturedExitDoS_DOS002 is Test {
    CarthaVaultFactory factory;
    ICarthaParentVault parentVault;
    ICarthaVault childA; // plain idle-USDC child
    ICarthaVault childB; // 0xM-deployed child — its USDC is moved into GM and becomes non-idle
    MockERC20 usdc;
    MockERC20 gmToken;
    MockExchangeRouter exchangeRouter;
    Mock0xMReader reader;
    Mock0xMOracle oracle;
    Diamond diamond;
    ICarthaAccessControl accessControl;

    address admin = address(0x1);
    address keeperBot = address(0x2);
    address incumbent = address(0x1001); // matured LP that wants to exit

    bytes32 categoryMetals = keccak256("metals");
    bytes32 poolIdGold = keccak256("XAU/USD");
    bytes32 poolIdSilver = keccak256("XAG/USD");
    uint64 constant LOCK_DAYS = 30;

    function setUp() public {
        vm.startPrank(admin);

        (diamond, accessControl) = DiamondTestUtils.deployDiamond(admin);
        accessControl.grantRole(Roles.FACTORY, admin);
        accessControl.grantRole(Roles.KEEPER_BOT, keeperBot);
        accessControl.grantRole(Roles.ADMIN, admin);

        CarthaVault childVaultImpl = new CarthaVault();
        UpgradeableBeacon childBeacon = new UpgradeableBeacon(address(childVaultImpl), admin);
        CarthaParentVault parentVaultImpl = new CarthaParentVault();
        UpgradeableBeacon parentBeacon = new UpgradeableBeacon(address(parentVaultImpl), admin);
        CarthaVaultFactory factoryImpl = new CarthaVaultFactory();
        bytes memory init = abi.encodeWithSelector(
            CarthaVaultFactory.initialize.selector, address(childBeacon), address(parentBeacon), address(diamond)
        );
        factory = CarthaVaultFactory(address(new ERC1967Proxy(address(factoryImpl), init)));

        usdc = new MockERC20("USD Coin", "USDC", 6);
        gmToken = new MockERC20("GM XAG/USD", "GM", 18);
        exchangeRouter = new MockExchangeRouter(address(gmToken));
        reader = new Mock0xMReader();
        oracle = new Mock0xMOracle();

        address aAddr = factory.deployVault(
            ICarthaVaultFactory.VaultConfig({asset: address(usdc), poolId: poolIdGold, name: "cvA", symbol: "cvA"})
        );
        address bAddr = factory.deployVault(
            ICarthaVaultFactory.VaultConfig({asset: address(usdc), poolId: poolIdSilver, name: "cvB", symbol: "cvB"})
        );
        childA = ICarthaVault(aAddr);
        childB = ICarthaVault(bAddr);

        address parentAddr = factory.deployParentVault(
            ICarthaVaultFactory.ParentVaultConfig({
                asset: address(usdc),
                category: categoryMetals,
                name: "Cartha Metals Vault",
                symbol: "cvMETALS"
            })
        );
        parentVault = ICarthaParentVault(parentAddr);

        accessControl.grantRole(Roles.ADMIN, address(factory));
        factory.addChildToParent(address(parentVault), address(childA), 50, 7000);
        factory.addChildToParent(address(parentVault), address(childB), 50, 7000);
        accessControl.grantRole(Roles.KEEPER_BOT, address(parentVault));
        CarthaParentVault(address(parentVault)).setParentMinimumLockAmount(1);

        // Wire child B for 0xM, GM valued CORRECTLY (1:1 mint + 1e30 reader price).
        childB.setPoolToken(address(gmToken));
        childB.setMarketToken(address(gmToken));
        childB.setExchangeRouter(address(exchangeRouter));
        childB.setDepositVault(address(gmToken));
        childB.setWithdrawalVault(address(gmToken));
        CarthaVault(address(childB)).setReader(address(reader));
        CarthaVault(address(childB)).setDataStore(address(0xDA7A));
        CarthaVault(address(childB)).setOracle(address(oracle));
        reader.setMarket(
            I0xMReader.MarketProps({
                marketToken: address(gmToken),
                indexToken: address(0xB7C),
                longToken: address(usdc),
                shortToken: address(usdc)
            })
        );
        reader.setMarketTokenPrice(int256(1e30));
        oracle.setPrice(address(0xB7C), 1e30, 1e30);
        oracle.setPrice(address(usdc), 1e30, 1e30);

        vm.stopPrank();
    }

    function _fund(address u, uint256 amt) internal {
        usdc.mint(u, amt);
        vm.prank(u);
        usdc.approve(address(parentVault), type(uint256).max);
    }

    function test_MaturedLP_CannotFullExit_WhenFundsGMDeployed() public {
        // 1) Incumbent LP locks $1,000,000 -> $500k to each child.
        _fund(incumbent, 1_000_000e6);
        vm.prank(incumbent);
        parentVault.depositAndLockSpread(1_000_000e6, LOCK_DAYS);

        // 2) Keeper deploys ALL of child B's idle USDC into the 0xM pool (no deploy-ratio cap is set).
        //    child B now holds $500k of GM and ZERO idle USDC.
        vm.prank(keeperBot);
        bytes32 key = childB.deployToPool(500_000e6, 0);
        exchangeRouter.executeDeposit(key, address(usdc));
        assertEq(usdc.balanceOf(address(childB)), 0, "child B has no idle USDC (all in GM)");
        assertGt(gmToken.balanceOf(address(childB)), 0, "child B holds GM");

        // 3) The value is all still there: totalAssets() == $1,000,000.
        uint256 tvl = parentVault.totalAssets();
        assertApproxEqAbs(tvl, 1_000_000e6, 10, "parent TVL still ~= $1,000,000 (value present)");
        console2.log("parent totalAssets() (value present): ", tvl);

        // 4) Time passes: BOTH the lock AND the cooldown expire -> the position is fully matured.
        vm.warp(block.timestamp + uint256(LOCK_DAYS) * 1 days + 1);

        // 5) THE DoS: the matured LP cannot withdraw their full position. Only child A's $500k idle is
        //    "available"; child B's $500k is GM-deployed and uncounted by _availableFromChildren().
        vm.prank(incumbent);
        vm.expectRevert(); // InsufficientVaultBalance
        parentVault.releaseFromParent(1_000_000e6);
        console2.log("full release reverted (matured LP cannot exit)");

        // 5b) The keeper batch path also yields NOTHING: processQueuedParentWithdrawals `continue`s on
        //     insufficient liquidity, so the queued matured LP is silently skipped (no payout).
        vm.prank(incumbent);
        parentVault.requestReleaseFromParent();
        address[] memory owners = new address[](1);
        owners[0] = incumbent;
        vm.prank(keeperBot);
        parentVault.processQueuedParentWithdrawals(owners);
        assertEq(usdc.balanceOf(incumbent), 0, "queued matured LP received NOTHING");
        assertGt(IERC20(address(parentVault)).balanceOf(incumbent), 0, "LP still holds all parent shares");
        console2.log("queued withdrawal settled $0 (keeper batch also bricks)");

        // 5c) NO permissionless escape: the LP cannot recall the GM themselves (KEEPER_BOT-only).
        vm.prank(incumbent);
        vm.expectRevert(); // onlyRole(KEEPER_BOT)
        CarthaVault(address(childB)).recallFromPool(1, 0);
        console2.log("LP cannot self-recall (recallFromPool is KEEPER_BOT-only)");

        // 6) CONTROL (causation): a trusted keeper recalls child B's GM -> idle USDC restored ->
        //    the matured LP can finally exit in full. The funds were gated solely on keeper liveness.
        uint256 gmBal = gmToken.balanceOf(address(childB));
        vm.prank(keeperBot);
        bytes32 wKey = CarthaVault(address(childB)).recallFromPool(gmBal, 0);
        exchangeRouter.executeWithdrawal(wKey, address(usdc));
        assertApproxEqAbs(usdc.balanceOf(address(childB)), 500_000e6, 10, "child B idle USDC restored");

        // Re-request (the prior request was consumed/!pending after the skipped settle? re-state cleanly):
        vm.prank(incumbent);
        parentVault.releaseFromParent(1_000_000e6); // now succeeds
        assertApproxEqAbs(usdc.balanceOf(incumbent), 1_000_000e6, 1_000, "LP finally exits in full after keeper recall");
        console2.log("after keeper recall, LP exits in full:", usdc.balanceOf(incumbent));
    }
}
