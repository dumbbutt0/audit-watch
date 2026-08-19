# CARTHA-SEAM-001 — gmValueInUsdc returns an 18-decimal USD value but is summed with 6-decimal USDC in TVL, inflating totalAssets ~1e12x once GM is held

- **Severity (recommended):** Critical
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** poc_required
- **Confidence:** High
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/libraries/PoolDeployLib.sol:108 ['/home/dummy/clones/cartha-vaults-main/src/CarthaVault.sol:940', '/home/dummy/clones/cartha-vaults-main/src/CarthaVault.sol:921', '/home/dummy/clones/cartha-vaults-main/src/CarthaVault.sol:932', '/home/dummy/clones/cartha-vaults-main/src/CarthaVault.sol:918']`
- **Vulnerable files (bundled in `sources/`):** `PoolDeployLib.sol`, `CarthaVault.sol`

## Description

Cartha's PoolDeployLib.gmValueInUsdc computes (gmBalance * gmPrice) / GM_PRICE_PRECISION (PoolDeployLib.sol:108). gmBalance is the vault's GM market-token balance at 18 decimals (0xMarkets MarketToken inherits OZ ERC20 with no decimals() override -> 18 dp, MarketToken.sol:12). gmPrice is the GMX/0xMarkets marketTokenPrice with units of 1e30 USD per 1 GM token (MarketUtils.getMarketTokenPrice = mulDiv(WEI_PRECISION=1e18, poolValue[1e30], supply[1e18]) -> (USD/token)*1e30; FLOAT_PRECISION=1e30 in Precision.sol:22). Dividing by GM_PRICE_PRECISION=1e30 therefore yields a USD value scaled to 1e18, NOT to 6-decimal USDC, despite the function name. CarthaVault._totalValueLocked() then adds this 1e18-scaled value directly to IERC20(asset).balanceOf(this), which for 6-decimal USDC is 1e6-scaled (CarthaVault.sol:940). The two addends are 12 orders of magnitude apart; the GM leg is ~1e12x over-weighted. The empty-pool share mint assets*10**(18-6) (CarthaVault.sol:918) confirms the intended unit of _totalValueLocked is 6-decimal USDC. PRICE-SCALE PROOF (reviewer challenge): GMX has two price scales — oracle INPUT prices are token-decimal-adjusted (1e30/10^dec, so USDC=1e24), but getMarketTokenPrice OUTPUT is re-based to 1e30 per WHOLE token by the WEI_PRECISION=1e18 multiplier; the supply==0 branch returns FLOAT_PRECISION=1e30 commented 'treat the market token price as 1 USD' (MarketUtils.sol:156-163), proving 1e30=$1/GM. So gmBalance(18-dec)*1e30/1e30 = an 18-dec USD figure -> +1e12 vs 6-dec USDC. PoC test_RealReaderPriceScale_Is1e30PerWholeToken replays the real formula to prove this from first principles. ATTACKER = a permissionless depositor who deposits AFTER a normal keeper deployToPool (the attacker does not trigger the deployment); the profiting holder is anyone who deposited before it.

## Impact

-

## Reachability / follow-up

reachable: yes — triggers on the first deployToPool execution (core feature) then on any permissionless depositAndLock / release. no_privileged_keys: deposit & release are permissionless; only the deploy is KEEPER (normal operation). state_before_after: pre-deploy TVL=idle(6-dec); once GM minted gmValueInUsdc adds an 18-dec term so TVL jumps ~1e12x for the same real value. why_guards_fail: no decimal normalization between the GM leg and the USDC leg; the test fixture equalizes 6-dec and 18-dec amounts so it never exercises the real scaling. scope_match: core share accounting.

## Triage reasoning

gmValueInUsdc() returns gmBalance(18-dec GM) * gmPrice(1e30 precision) / 1e30, which is an 18-DECIMAL USD figure, and _totalValueLocked() adds it directly to the 6-decimal USDC balanceOf with no 1e12 normalization. Confirmed against canonical GMX (getMarketTokenPrice scales exactly this way; 0xMarkets is verbatim GMX here). The moment any USDC is deployed to a pool and GM is held, TVL is inflated ~1e12x, so _convertToShares under-mints new depositors ~1e12x and _convertToAssets makes existing shares appear ~1e12x over-valued -> release() reverts (InsufficientVaultBalance, funds frozen) and depositors during the GM-held window permanently lose principal to pre-deploy holders. The only unit test that touches this passes solely because its mock mints GM numerically equal to the 6-dec USDC amount, masking the mismatch. Merges AR-001 (same root cause: the gmBalance*gmPrice/1e30 GM-leg scaling — over-count face here, truncation-to-0 face there).
