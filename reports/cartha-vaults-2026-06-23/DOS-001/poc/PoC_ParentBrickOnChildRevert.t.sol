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
 * @title RevertingReader — stands in for a 0xM Reader whose GM price read reverts
 * @notice The production GM valuation path (PoolDeployLib._getGmPrice) makes several unguarded
 *         external calls into 0xMarkets: reader.getMarket(), oracle.getPrimaryPrice() x3, and
 *         reader.getMarketTokenPrice(). Any of these reverts under ordinary 0xMarkets conditions —
 *         e.g. the oracle has no primary price for the token in the current block (EmptyPrimaryPrice),
 *         the market is disabled, or getMarketTokenPrice hits a pool-value/arithmetic edge. This mock
 *         reproduces exactly that: a Reader whose reads revert. No admin action is needed in
 *         production for the real Reader to revert under these conditions; swapping the reader here is
 *         only the test mechanism to put the child into that already-reachable state.
 */
contract RevertingReader is I0xMReader {
    error ReaderUnavailable();

    function getMarket(address, address) external pure returns (MarketProps memory) {
        revert ReaderUnavailable();
    }

    function getMarketTokenPrice(
        address,
        MarketProps memory,
        PriceProps memory,
        PriceProps memory,
        PriceProps memory,
        bytes32,
        bool
    ) external pure returns (int256, MarketPoolValueInfoProps memory) {
        revert ReaderUnavailable();
    }
}

/**
 * @title PoC — DOS-001 : one child's reverting GM price read bricks ALL parent operations
 *
 * @notice CarthaParentVault.totalAssets() loops over every active child and calls
 *         child.totalValueLocked() with NO try/catch (CarthaParentVault.sol:351-365). A child that
 *         holds GM values it via PoolDeployLib._getGmPrice, which makes unguarded external calls into
 *         the 0xMarkets Reader/Oracle (PoolDeployLib.sol:111-127). If ANY one child's GM read reverts,
 *         the whole totalAssets() loop reverts — and because every parent entry/exit path
 *         (depositAndLockSpread -> _convertToShares, releaseFromParent / processQueuedParentWithdrawals
 *         / executeForceExit -> _prepareSharePayout) reads totalAssets(), the entire parent is frozen
 *         for ALL LPs until that single child's read recovers. One bad child poisons the whole pool.
 *
 * @dev INDEPENDENCE: this is a liveness / fault-isolation bug, distinct from CARTHA-SEAM-001 (GM
 *      decimal scale) and DT-001 (in-flight accounting window). The GM here is valued CORRECTLY
 *      (default 1:1 mint + 1e30 reader price) in the healthy baseline; the freeze comes purely from
 *      the missing try/catch around the cross-child external call. It survives both other fixes.
 */
contract PoC_ParentBrickOnChildRevert is Test {
    CarthaVaultFactory factory;
    ICarthaParentVault parentVault;
    ICarthaVault childA; // plain idle-USDC child (gold) — never touches 0xM
    ICarthaVault childB; // deploys to 0xM and holds GM (silver) — its reader will revert
    MockERC20 usdc;
    MockERC20 gmToken;
    MockExchangeRouter exchangeRouter;
    Mock0xMReader reader;
    Mock0xMOracle oracle;
    Diamond diamond;
    ICarthaAccessControl accessControl;

    address admin = address(0x1);
    address keeperBot = address(0x2);
    address incumbent = address(0x1001); // LP locked in the parent, wants to exit
    address newLp = address(0x1002); // LP that wants to enter after the freeze

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

        // Two children: A = plain idle USDC, B = 0xM-deployed (holds GM)
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
        factory.addChildToParent(address(parentVault), address(childA), 50, 7000); // 50%
        factory.addChildToParent(address(parentVault), address(childB), 50, 7000); // 50%
        accessControl.grantRole(Roles.KEEPER_BOT, address(parentVault));
        CarthaParentVault(address(parentVault)).setParentMinimumLockAmount(1);

        // Wire ONLY child B for 0xM. GM valued CORRECTLY: default 1:1 mint + 1e30 reader price, so
        // gmValueInUsdc returns the true USDC value (this is NOT the SEAM decimal bug).
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

    function test_OneChildRevert_BricksAllParentOps() public {
        // 1) Incumbent LP locks $1,000,000 in the parent -> split $500k to each child.
        _fund(incumbent, 1_000_000e6);
        vm.prank(incumbent);
        parentVault.depositAndLockSpread(1_000_000e6, LOCK_DAYS);

        // 2) Keeper deploys half of child B's idle USDC into the 0xM pool; the 0xM keeper then
        //    executes the deposit -> child B now HOLDS GM (so its GM price-read path is live).
        vm.prank(keeperBot);
        bytes32 key = childB.deployToPool(250_000e6, 0);
        exchangeRouter.executeDeposit(key, address(usdc));
        assertGt(gmToken.balanceOf(address(childB)), 0, "child B holds GM");

        // 3) BASELINE (healthy): the parent prices fine and is fully operational.
        uint256 healthyTVL = parentVault.totalAssets();
        assertApproxEqAbs(healthyTVL, 1_000_000e6, 10, "healthy parent TVL ~= $1,000,000");
        console2.log("healthy parent totalAssets() :", healthyTVL);

        // Queue a withdrawal while healthy (requestReleaseFromParent does NOT read totalAssets()).
        vm.warp(block.timestamp + uint256(LOCK_DAYS) * 1 days + 1);
        vm.prank(incumbent);
        parentVault.requestReleaseFromParent();

        // 4) INJECT THE FAULT: child B's GM read now reverts (oracle stale / market disabled / etc.).
        //    No parent state is touched; only the external Reader becomes unavailable.
        RevertingReader reverter = new RevertingReader();
        vm.prank(admin);
        CarthaVault(address(childB)).setReader(address(reverter));

        // 5) DoS: ONE child's reverting read now bricks EVERY parent operation.

        // 5a) Pricing itself is dead.
        vm.expectRevert();
        parentVault.totalAssets();

        // 5b) The locked incumbent can no longer exit (funds frozen).
        vm.prank(incumbent);
        vm.expectRevert();
        parentVault.releaseFromParent(1_000_000e6);

        // 5c) The keeper's batch settlement of the queued withdrawal also bricks.
        address[] memory owners = new address[](1);
        owners[0] = incumbent;
        vm.prank(keeperBot);
        vm.expectRevert();
        parentVault.processQueuedParentWithdrawals(owners);

        // 5d) New LPs cannot even enter.
        _fund(newLp, 100_000e6);
        vm.prank(newLp);
        vm.expectRevert();
        parentVault.depositAndLockSpread(100_000e6, LOCK_DAYS);

        // 5e) Proof the FAULT IS ISOLATED TO THE PARENT-LEVEL LOOP, not child A: child A's own
        //     totalValueLocked() still succeeds. A single sibling's failure poisons the whole parent.
        uint256 childATVL = childA.totalValueLocked();
        assertGt(childATVL, 0, "healthy sibling child A still prices fine on its own");
        console2.log("healthy sibling child A TVL  :", childATVL);

        // 6) CONTROL (causation): restore child B's reader -> the parent is fully operational again,
        //    proving child B's revert (not unrelated state) was the sole cause of the freeze.
        vm.prank(admin);
        CarthaVault(address(childB)).setReader(address(reader));
        uint256 recoveredTVL = parentVault.totalAssets();
        assertApproxEqAbs(recoveredTVL, healthyTVL, 10, "parent fully recovers once the child read works again");
        console2.log("recovered parent totalAssets():", recoveredTVL);

        // A real user op succeeds again post-recovery. (Partial $500k: only the ~$750k of idle USDC
        // across children is liquid — child B's $250k is in GM — so we release within liquidity; the
        // full-exit-with-deployed-GM liquidity gap is a separate finding, not DOS-001.)
        vm.prank(incumbent);
        parentVault.releaseFromParent(500_000e6); // now succeeds
        console2.log("incumbent partial exit (USDC) :", usdc.balanceOf(incumbent));
    }
}
