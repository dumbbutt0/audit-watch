// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console2} from "forge-std/Test.sol";
import {ERC1967Proxy} from "openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {UpgradeableBeacon} from "openzeppelin-contracts/contracts/proxy/beacon/UpgradeableBeacon.sol";
import {IERC20} from "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import {CarthaVaultFactory} from "../src/CarthaVaultFactory.sol";
import {CarthaVault} from "../src/CarthaVault.sol";
import {CarthaParentVault} from "../src/CarthaParentVault.sol";
import {Diamond} from "../src/diamond/Diamond.sol";
import {MockERC20} from "../test/mocks/MockERC20.sol";
import {MockExchangeRouter} from "../test/mocks/MockExchangeRouter.sol";
import {Mock0xMReader} from "../test/mocks/Mock0xMReader.sol";
import {Mock0xMOracle} from "../test/mocks/Mock0xMOracle.sol";
import {I0xMReader} from "../src/interfaces/I0xMReader.sol";
import {DiamondTestUtils} from "../test/utils/DiamondTestUtils.sol";
import {ICarthaVaultFactory} from "../src/interfaces/ICarthaVaultFactory.sol";
import {ICarthaVault} from "../src/interfaces/ICarthaVault.sol";
import {ICarthaParentVault} from "../src/interfaces/ICarthaParentVault.sol";
import {ICarthaAccessControl} from "../src/interfaces/ICarthaAccessControl.sol";
import {Roles} from "../src/diamond/Roles.sol";

// --- REAL in-scope 0xMarkets (GMX-v2 fork) contracts, compiled from the bounty repo ---
import {RoleStore} from "zeromark/role/RoleStore.sol";
import {DataStore} from "zeromark/data/DataStore.sol";
import {EventEmitter} from "zeromark/event/EventEmitter.sol";
import {Oracle} from "zeromark/oracle/Oracle.sol";
import {Errors as OxMErrors} from "zeromark/error/Errors.sol";
import {AggregatorV2V3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV2V3Interface.sol";

/**
 * @title DOS-001 (INTEGRATED) — a GENUINE 0xMarkets oracle revert bricks ALL parent operations
 *
 * @notice This is the hardened variant of `test/poc/PoC_ParentBrickOnChildRevert.t.sol`. The
 *         original models the fault with a hand-written `RevertingReader` stand-in; a skeptical
 *         reviewer could ask "does the real 0xMarkets reader/oracle actually revert in practice?"
 *
 *         This version removes the stand-in entirely. It deploys the **real, in-scope 0xMarkets
 *         `Oracle`** (the exact GMX-v2-fork contract from the bounty repo, compiled here:
 *         `contracts/oracle/Oracle.sol`) and routes child B's pricing oracle to it. When no primary
 *         price is set for the index token in the current block — the ordinary case for a view price
 *         read outside an oracle-priced keeper transaction — the real `Oracle.getPrimaryPrice`
 *         reverts the real `Errors.EmptyPrimaryPrice`. That genuine revert, fired through Cartha's
 *         real `PoolDeployLib._getGmPrice`, propagates through `CarthaParentVault.totalAssets()`'s
 *         unguarded cross-child loop (no try/catch) and freezes every parent entry/exit path.
 *
 * @dev The headline assertion is exact: `parentVault.totalAssets()` reverts with the real
 *      `EmptyPrimaryPrice(indexToken)` selector — i.e. the in-scope 0xMarkets error surfaces verbatim
 *      at the parent boundary. GM is valued CORRECTLY in the healthy baseline (this is not the SEAM
 *      decimal bug, and not DT-001's accounting window); the freeze is purely the missing isolation.
 */
contract PoC_RealOxMOracleRevert_BricksParent is Test {
    CarthaVaultFactory factory;
    ICarthaParentVault parentVault;
    ICarthaVault childA; // plain idle-USDC child (never touches 0xM)
    ICarthaVault childB; // deploys to 0xM and holds GM — priced through the real Oracle
    MockERC20 usdc;
    MockERC20 gmToken;
    MockExchangeRouter exchangeRouter;
    Mock0xMReader reader; // returns the market's token addresses (getMarket); healthy pricing only
    Mock0xMOracle mockOracle; // healthy baseline oracle (returns valid prices)
    Diamond diamond;
    ICarthaAccessControl accessControl;

    // Real in-scope 0xMarkets oracle stack
    Oracle realOracle;

    address admin = address(0x1);
    address keeperBot = address(0x2);
    address incumbent = address(0x1001);
    address newLp = address(0x1002);

    bytes32 categoryMetals = keccak256("metals");
    bytes32 poolIdGold = keccak256("XAU/USD");
    bytes32 poolIdSilver = keccak256("XAG/USD");
    uint64 constant LOCK_DAYS = 30;

    // The child B market's index token. The real Oracle is deployed with NO price for it, so a read
    // reverts EmptyPrimaryPrice(INDEX_TOKEN) — exactly as in production outside an oracle-priced tx.
    address constant INDEX_TOKEN = address(0xB7C);

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
        mockOracle = new Mock0xMOracle();

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

        // Wire ONLY child B for 0xM. Healthy baseline prices GM CORRECTLY via the mock oracle
        // (1e30 reader price + 1:1 mint => true USDC value). This is NOT the SEAM decimal bug.
        childB.setPoolToken(address(gmToken));
        childB.setMarketToken(address(gmToken));
        childB.setExchangeRouter(address(exchangeRouter));
        childB.setDepositVault(address(gmToken));
        childB.setWithdrawalVault(address(gmToken));
        CarthaVault(address(childB)).setReader(address(reader));
        CarthaVault(address(childB)).setDataStore(address(0xDA7A));
        CarthaVault(address(childB)).setOracle(address(mockOracle));
        reader.setMarket(
            I0xMReader.MarketProps({
                marketToken: address(gmToken),
                indexToken: INDEX_TOKEN,
                longToken: address(usdc),
                shortToken: address(usdc)
            })
        );
        reader.setMarketTokenPrice(int256(1e30));
        mockOracle.setPrice(INDEX_TOKEN, 1e30, 1e30);
        mockOracle.setPrice(address(usdc), 1e30, 1e30);

        vm.stopPrank();

        // Deploy the REAL in-scope 0xMarkets Oracle stack. No price is set for INDEX_TOKEN, so a read
        // reverts the genuine EmptyPrimaryPrice — no admin action and no stand-in contract required.
        RoleStore rs = new RoleStore();
        DataStore dstore = new DataStore(rs);
        EventEmitter ee = new EventEmitter(rs);
        realOracle = new Oracle(rs, dstore, ee, AggregatorV2V3Interface(address(0)));
    }

    function _fund(address u, uint256 amt) internal {
        usdc.mint(u, amt);
        vm.prank(u);
        usdc.approve(address(parentVault), type(uint256).max);
    }

    /// @notice Standalone realism check: the REAL in-scope Oracle reverts EmptyPrimaryPrice on an
    ///         unpriced, non-zero token — the exact production condition the brick relies on.
    function test_RealOracle_RevertsEmptyPrimaryPrice() public {
        vm.expectRevert(abi.encodeWithSelector(OxMErrors.EmptyPrimaryPrice.selector, INDEX_TOKEN));
        realOracle.getPrimaryPrice(INDEX_TOKEN);
    }

    function test_RealOxMOracleRevert_BricksAllParentOps() public {
        // 1) Incumbent LP locks $1,000,000 -> $500k to each child.
        _fund(incumbent, 1_000_000e6);
        vm.prank(incumbent);
        parentVault.depositAndLockSpread(1_000_000e6, LOCK_DAYS);

        // 2) Keeper deploys half of child B's idle USDC; the 0xM keeper executes -> child B HOLDS GM
        //    (its GM price-read path is now live).
        vm.prank(keeperBot);
        bytes32 key = childB.deployToPool(250_000e6, 0);
        exchangeRouter.executeDeposit(key, address(usdc));
        assertGt(gmToken.balanceOf(address(childB)), 0, "child B holds GM");

        // 3) BASELINE (healthy): the parent prices fine through the mock oracle and is fully operational.
        uint256 healthyTVL = parentVault.totalAssets();
        assertApproxEqAbs(healthyTVL, 1_000_000e6, 10, "healthy parent TVL ~= $1,000,000");
        console2.log("healthy parent totalAssets()  :", healthyTVL);

        // Queue a withdrawal while healthy (requestReleaseFromParent does NOT read totalAssets()).
        vm.warp(block.timestamp + uint256(LOCK_DAYS) * 1 days + 1);
        vm.prank(incumbent);
        parentVault.requestReleaseFromParent();

        // 4) INJECT THE GENUINE FAULT: point child B's oracle at the REAL in-scope 0xMarkets Oracle,
        //    which has no primary price for the index token -> a read reverts the real EmptyPrimaryPrice.
        //    No stand-in contract; this is the exact production revert path.
        vm.prank(admin);
        CarthaVault(address(childB)).setOracle(address(realOracle));

        // 5) DoS: the REAL EmptyPrimaryPrice now bricks EVERY parent operation.

        // 5a) HEADLINE — the in-scope 0xMarkets error selector surfaces verbatim at the parent boundary.
        vm.expectRevert(abi.encodeWithSelector(OxMErrors.EmptyPrimaryPrice.selector, INDEX_TOKEN));
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

        // 5e) ISOLATION: the healthy sibling child A still prices on its own. One sibling's failure
        //     poisons the whole parent purely via the unguarded cross-child loop.
        uint256 childATVL = childA.totalValueLocked();
        assertGt(childATVL, 0, "healthy sibling child A still prices fine on its own");
        console2.log("healthy sibling child A TVL   :", childATVL);

        // 6) CONTROL (causation): restore a working oracle -> the parent is fully operational again,
        //    proving the real Oracle's revert was the sole cause of the freeze.
        vm.prank(admin);
        CarthaVault(address(childB)).setOracle(address(mockOracle));
        uint256 recoveredTVL = parentVault.totalAssets();
        assertApproxEqAbs(recoveredTVL, healthyTVL, 10, "parent fully recovers once pricing works again");
        console2.log("recovered parent totalAssets():", recoveredTVL);

        // A real user op succeeds again post-recovery (partial $500k within the idle-USDC liquidity).
        vm.prank(incumbent);
        parentVault.releaseFromParent(500_000e6);
        console2.log("incumbent partial exit (USDC) :", usdc.balanceOf(incumbent));
    }
}
