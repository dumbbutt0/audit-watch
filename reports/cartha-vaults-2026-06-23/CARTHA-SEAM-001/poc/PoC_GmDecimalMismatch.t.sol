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
import {ICarthaErrors} from "../../src/interfaces/ICarthaErrors.sol";
import {ICarthaAccessControl} from "../../src/interfaces/ICarthaAccessControl.sol";
import {Roles} from "../../src/diamond/Roles.sol";

/**
 * @title PoC — CARTHA-SEAM-001 : GM valuation 1e12 decimal mismatch
 * @notice Re-verifies that PoolDeployLib.gmValueInUsdc() returns an 18-decimal USD value while
 *         CarthaVault._totalValueLocked() adds it directly to the 6-decimal USDC balance, inflating
 *         TVL by ~1e12 the moment any USDC is deployed to a 0xM pool, which corrupts all share math.
 *
 * @dev REAL-GMX MODELING (the re-verification core):
 *      - GM market token is 18 decimals (as in GMX v2). MockExchangeRouter mints
 *        gmAmount = usdcAmount * gmPriceDenominator / gmPriceNumerator. Setting setGmPrice(1, 1e12)
 *        mints the REALISTIC amount: 100_000e6 USDC ($100k) -> 100_000e18 GM at $1/GM, and round-trips
 *        back to 100_000e6 USDC on withdrawal.
 *      - Reader.getMarketTokenPrice returns 1e30 = $1 per WHOLE GM token. This is the price scale the
 *        seam consumes, and it is the reviewer's likely push-back, so it is PROVEN from the real source
 *        (not assumed) in test_RealReaderPriceScale_Is1e30PerWholeToken below.
 *      Then gmValueInUsdc = gmBal(1e18-scale) * 1e30 / 1e30 = an 18-decimal USD number.
 *
 *      TWO DIFFERENT GMX PRICE SCALES (conflating them is the dev's exact mistake):
 *        - Oracle INPUT prices are token-decimal-adjusted: price = 1e30 / 10^tokenDecimals, so USDC at $1
 *          = 1e24 and an 18-dec token at $1 = 1e12 (per *native unit*).
 *        - getMarketTokenPrice OUTPUT is re-based to 1e30 per *whole* GM token by the WEI_PRECISION(1e18)
 *          multiplier in MarketUtils.getMarketTokenPrice (so 1 GM at $1 = 1e30, NOT 1e12). The supply==0 branch
 *          returns FLOAT_PRECISION(1e30) with the comment "treat the market token price as 1 USD".
 *      Because gmBalance is in native (1e18) units and gmPrice is per-whole-token (1e30), dividing by only
 *      1e30 leaves an extra 1e18 factor -> an 18-decimal USD value -> +1e12 vs the 6-decimal USDC leg.
 *
 *      The repo's own suite (CarthaVaultPool.t.sol) MASKS this by leaving setGmPrice at 1:1, so the
 *      mock mints GM in 6-decimal magnitude — two wrongs that cancel. test_Control_* reproduces that.
 */
contract PoC_GmDecimalMismatch is Test {
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
    address user1 = address(0x1001); // pre-deploy depositor (incumbent)
    address user2 = address(0x1002); // post-deploy depositor (victim)

    bytes32 poolId = keccak256("BTC/USD");
    uint256 constant MIN_LOCK = 100_000e6; // 100k USDC
    uint64 constant LOCK_DAYS = 30;

    function _deployVaultAndConfig() internal {
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
        gmToken = new MockERC20("GM BTC/USD", "GM", 18); // GMX market tokens are 18-decimal
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
        reader.setMarketTokenPrice(int256(1e30)); // $1 per GM in GMX 30-decimal convention
        oracle.setPrice(address(0xB7C), 1e30, 1e30);
        oracle.setPrice(address(usdc), 1e30, 1e30);
        vm.stopPrank();
    }

    function _deposit(address u, uint256 amt) internal {
        usdc.mint(u, amt);
        vm.startPrank(u);
        usdc.approve(address(vault), amt);
        vault.depositAndLock(poolId, amt, LOCK_DAYS);
        vm.stopPrank();
    }

    function _deploy(uint256 amt) internal {
        vm.prank(keeperBot);
        bytes32 k = vault.deployToPool(amt, 0);
        exchangeRouter.executeDeposit(k, address(usdc));
    }

    function _recallAll() internal {
        uint256 gmBal = gmToken.balanceOf(address(vault));
        vm.prank(keeperBot);
        bytes32 k = vault.recallFromPool(gmBal, 0);
        exchangeRouter.executeWithdrawal(k, address(usdc));
    }

    function _expire() internal {
        vm.warp(block.timestamp + uint256(LOCK_DAYS) * 1 days + 7 days + 1);
    }

    /// CORE PROOF: with realistic 18-dec GM minting, gmValueInUsdc inflates TVL by exactly 1e12.
    function test_DecimalMismatch_InflatesTVL_1e12() public {
        _deployVaultAndConfig();
        exchangeRouter.setGmPrice(1, 1e12); // realistic: 100k USDC -> 100_000e18 GM at $1

        _deposit(user1, MIN_LOCK);
        assertEq(vault.totalValueLocked(), MIN_LOCK, "pre-deploy TVL = idle USDC (correct, 6-dec)");

        _deploy(MIN_LOCK); // USDC -> GM (vault now holds 100_000e18 GM, 0 USDC)

        assertEq(gmToken.balanceOf(address(vault)), 100_000e18, "realistic GMX: $100k -> 100_000e18 GM");
        assertEq(usdc.balanceOf(address(vault)), 0, "all USDC deployed");

        uint256 tvl = vault.totalValueLocked();
        uint256 trueValueUsdc = MIN_LOCK; // GM is still worth exactly $100k

        // gmValueInUsdc returned an 18-decimal number; TVL is 1e12x the real USDC value.
        assertEq(tvl, 100_000e18, "TVL reads the 18-decimal GM value verbatim");
        assertEq(tvl, trueValueUsdc * 1e12, "TVL inflated by exactly 1e12 vs true USDC value");
        console2.log("True value (USDC, 6dec):", trueValueUsdc);
        console2.log("Reported TVL          :", tvl);
    }

    /// IMPACT: a depositor entering while GM is held is under-credited 1e12x and loses principal to
    /// the pre-deploy holder, who can then withdraw BOTH deposits.
    function test_DecimalMismatch_LateDepositorLosesPrincipal() public {
        _deployVaultAndConfig();
        exchangeRouter.setGmPrice(1, 1e12);

        // 1) user1 deposits 100k BEFORE deploy -> minted at the correct 1e12 rate.
        _deposit(user1, MIN_LOCK);
        uint256 user1Shares = CarthaVault(address(vault)).balanceOf(user1);
        assertEq(user1Shares, MIN_LOCK * 1e12, "user1 minted at correct 1e12 rate");

        // 2) keeper deploys -> TVL inflates 1e12x.
        _deploy(MIN_LOCK);

        // 3) user2 deposits the SAME 100k while GM is held -> under-credited ~1e12x.
        _deposit(user2, MIN_LOCK);
        uint256 user2Shares = CarthaVault(address(vault)).balanceOf(user2);
        assertApproxEqRel(user1Shares / user2Shares, 1e12, 1e16, "user2 got ~1e12x FEWER shares for equal $");
        assertLt(user2Shares, user1Shares / 1e11, "user2 catastrophically under-credited");

        // 4) keeper recalls GM -> USDC; both deposits now idle (200k), GM=0, TVL correct again.
        _recallAll();
        assertEq(usdc.balanceOf(address(vault)), 2 * MIN_LOCK, "200k USDC now idle");
        _expire();

        // 5) user2 CANNOT recover principal: their share of TVL rounds to 0, so release reverts
        //    InsufficientVaultBalance (payout==0 guard). Their $100k is stuck.
        vm.prank(user2);
        vm.expectRevert(ICarthaErrors.InsufficientVaultBalance.selector);
        vault.release(poolId, MIN_LOCK);
        assertEq(usdc.balanceOf(user2), 0, "victim cannot withdraw any of their $100k deposit");
        console2.log("user2 deposited (USDC):", MIN_LOCK);
        console2.log("user2 recovered (USDC): 0 (release reverts)");

        // 6) user1 (incumbent) releases -> drains essentially BOTH deposits (~200k).
        vm.prank(user1);
        vault.release(poolId, MIN_LOCK);
        uint256 user1Out = usdc.balanceOf(user1);
        assertGt(user1Out, MIN_LOCK + (MIN_LOCK * 99 / 100), "incumbent withdraws ~both deposits (~200k)");
        console2.log("user1 deposited (USDC):", MIN_LOCK);
        console2.log("user1 recovered (USDC):", user1Out);
    }

    /// UNIT PROOF (answers "prove the real reader returns 1e30"): replicate the EXACT formula in
    /// 0xMarkets MarketUtils.getMarketTokenPrice — marketTokenPrice = mulDiv(WEI_PRECISION, poolValue, supply)
    /// (contracts/market/MarketUtils.sol:163; WEI_PRECISION=1e18, FLOAT_PRECISION=1e30 in utils/Precision.sol)
    /// — with realistic GMX-scale inputs, and show it yields 1e30 for a $1 GM token. MarketToken is a plain
    /// 18-decimal ERC20 (no decimals() override). This is the price the seam feeds into gmValueInUsdc.
    function test_RealReaderPriceScale_Is1e30PerWholeToken() public pure {
        uint256 WEI_PRECISION = 1e18;   // Precision.WEI_PRECISION
        uint256 FLOAT_PRECISION = 1e30; // Precision.FLOAT_PRECISION ("1 USD")

        // A pool worth $1,000,000. GMX poolValue is USD in 30-decimal precision -> 1_000_000 * 1e30.
        uint256 poolValue = 1_000_000 * FLOAT_PRECISION; // 1e36
        // 1,000,000 GM market tokens minted (MarketToken = 18-dec ERC20) -> supply in native units.
        uint256 supply = 1_000_000 * 1e18; // 1e24  => each GM is worth exactly $1

        // marketTokenPrice = WEI_PRECISION * poolValue / supply   (MarketUtils.sol:163)
        uint256 marketTokenPrice = WEI_PRECISION * poolValue / supply;
        assertEq(marketTokenPrice, 1e30, "real getMarketTokenPrice scale: $1/GM == 1e30 per whole token");

        // The supply==0 branch (MarketUtils.sol:156-159) returns FLOAT_PRECISION and is commented
        // "treat the market token price as 1 USD" -> 1e30 == $1, the same scale.
        assertEq(FLOAT_PRECISION, 1e30, "supply==0 convention: 1e30 == $1 per market token");

        // Therefore the seam's gmValueInUsdc = gmBalance(native 18-dec) * 1e30 / 1e30 is an 18-dec USD
        // figure. For 100k GM that is 100_000e18, vs the true 6-dec USDC value 100_000e6 -> 1e12 too big.
        uint256 gmBalance = 100_000e18;                 // 100k GM in native units
        uint256 seamValue = gmBalance * marketTokenPrice / 1e30; // PoolDeployLib.sol:108
        assertEq(seamValue, 100_000e18, "seam returns an 18-decimal USD value");
        assertEq(seamValue, (100_000e6) * 1e12, "exactly 1e12 larger than the true 6-decimal USDC value");
    }

    /// CONTROL: the repo's default 1:1 mock mint (GM minted in 6-dec magnitude) hides the bug.
    function test_Control_6DecMintNoInflation() public {
        _deployVaultAndConfig();
        // setGmPrice stays at the default 1:1 -> mock mints 100_000e6 GM (6-dec magnitude, UNREALISTIC)
        _deposit(user1, MIN_LOCK);
        _deploy(MIN_LOCK);
        assertEq(gmToken.balanceOf(address(vault)), MIN_LOCK, "default mock mints GM in 6-dec magnitude");
        // The two errors cancel: TVL looks correct, which is why the suite never caught the bug.
        assertEq(vault.totalValueLocked(), MIN_LOCK, "masked: TVL appears correct under the 1:1 mock");
    }
}
