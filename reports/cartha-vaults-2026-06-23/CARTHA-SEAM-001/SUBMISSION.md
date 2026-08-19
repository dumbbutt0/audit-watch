# CARTHA-SEAM-001 — GM-token valuation has a 1e12 decimal mismatch, breaking all share accounting and causing depositor principal loss

| | |
|---|---|
| **Severity** | **Critical** (direct loss of user principal; corrupts every share mint/redeem) |
| **Category (HackenProof VRT)** | Business Logic Errors |
| **Target** | Cartha Vaults (`cartha-vaults-main`, commit `4c51f2a8915f438976b57134d646b55199a11318`) |
| **Contracts** | `src/libraries/PoolDeployLib.sol`, `src/CarthaVault.sol` |
| **Activation** | Triggered by **normal operation**, not by the attacker: once a keeper performs a routine `deployToPool` of idle USDC into a 0xMarkets pool (the core yield feature), the vault holds GM and TVL is corrupted. |
| **Attacker** | A **permissionless depositor who deposits after a normal keeper deployment** — no privileged role and no ability to influence the keeper required. The holder who profits is simply anyone who deposited *before* the deployment. |
| **PoC** | `poc/PoC_GmDecimalMismatch.t.sol` (4/4 passing — `poc/run_output.txt`) |

## Summary

A child `CarthaVault` values its USDC (`asset`, **6 decimals**) and its GM market tokens (**18 decimals**) on the same scale when computing Total Value Locked, but the GM leg is never normalized. `PoolDeployLib.gmValueInUsdc()` returns an **18-decimal** USD figure (GM balance × the 1e30-precision GMX market-token price ÷ `1e30`), and `CarthaVault._totalValueLocked()` adds that **directly** to the 6-decimal USDC balance. The moment any USDC is deployed to a 0xMarkets pool and the vault holds GM, TVL is overstated by a factor of **1e12** (`10^(18-6)`), which corrupts `_convertToShares`/`_convertToAssets` and the entire share price.

## Vulnerability detail

`PoolDeployLib.sol` (the GM valuation seam):

```solidity
uint256 internal constant GM_PRICE_PRECISION = 1e30;

function gmValueInUsdc(address poolToken, address reader, address dataStore, address market, address oracle)
    external view returns (uint256)
{
    uint256 gmBalance = poolToken != address(0) ? IERC20(poolToken).balanceOf(address(this)) : 0; // 18-dec units
    if (gmBalance == 0 || reader == address(0)) return 0;
    int256 gmPrice = _getGmPrice(reader, dataStore, market, oracle);                               // 1e30 USD/GM
    if (gmPrice <= 0) return 0;
    return (gmBalance * uint256(gmPrice)) / GM_PRICE_PRECISION;   // == 18-decimal USD, NOT 6-decimal USDC
}
```

For GM at $1: GMX returns `gmPrice = 1e30`, so `gmValueInUsdc = gmBalance(1e18-scale) * 1e30 / 1e30 = gmBalance` — an 18-decimal number. The function name promises "USDC" (6 decimals) but returns an 18-decimal value.

### Unit proof — the reader really returns `1e30` per *whole* GM token (the key reviewer challenge)

The one thing that must be nailed down is the scale of `gmPrice`. GMX has **two different price conventions**, and conflating them is precisely the dev's mistake:

- **Oracle *input* prices** *are* token-decimal-adjusted: `price = 1e30 / 10^tokenDecimals`. So USDC ($1, 6-dec) is `1e24` and an 18-dec token ($1) is `1e12`, *per native unit*. (This is the convention a reviewer rightly points to.)
- **`getMarketTokenPrice` *output* is NOT** that convention. It is re-based to **`1e30` per *whole* GM token**, and this is provable directly from the in-scope 0xMarkets source:

```solidity
// 0xMarkets contracts/market/MarketUtils.sol  (the reader PoolDeployLib calls)
// L156-159 — definitional:
//   "if the supply is zero then treat the market token price as 1 USD"
if (supply == 0) { return (Precision.FLOAT_PRECISION.toInt256(), poolValueInfo); } // FLOAT_PRECISION = 1e30
// L163 — general case:
int256 marketTokenPrice = Precision.mulDiv(Precision.WEI_PRECISION, poolValueInfo.poolValue, supply);
// Precision.sol: WEI_PRECISION = 1e18 , FLOAT_PRECISION = 1e30
```

The `supply == 0` branch returns `FLOAT_PRECISION` (`1e30`) and the code comments it as **"1 USD"** — so by the protocol's own definition, **`1e30 = $1 per market token`**. The general branch is consistent: `poolValue` is USD in 30-dec precision and `supply` is in 18-dec native units, so for a $1M pool with 1M GM tokens, `marketTokenPrice = 1e18 × (1e6·1e30) / (1e6·1e18) = 1e30`. The `WEI_PRECISION` (1e18) multiplier is exactly what re-bases the price to *per whole token* rather than *per native unit* — which is why a $1 GM is `1e30`, not the `1e12` an oracle-style per-native-unit price would give. `MarketToken` is a plain 18-decimal OpenZeppelin ERC20 (no `decimals()` override), confirming the 18-dec native scale.

**Putting it together (dimensional analysis):**

```
gmValueInUsdc = gmBalance [native, 18-dec]  ×  gmPrice [USD/whole-token × 1e30]  /  1e30
              = (whole GM × 1e18) × (USD/whole × 1e30) / 1e30
              = USD × 1e18          ← an 18-DECIMAL USD figure
```

Summed with the 6-decimal USDC balance, the GM leg is larger by `10^(18 − 6) = 1e12`. This is asserted directly in the PoC (`test_RealReaderPriceScale_Is1e30PerWholeToken`) by replaying the exact `MarketUtils.sol:163` formula on realistic GMX-scale inputs and showing the result is `1e30` for $1/GM and that the seam then yields `100_000e18` for 100k GM (vs the true `100_000e6`).

`CarthaVault.sol` then sums it with 6-decimal USDC, with no `1e12` normalization:

```solidity
function _totalValueLocked() internal view returns (uint256) {
    CarthaVaultStorage storage $ = _getCarthaVaultStorage();
    return IERC20($.asset).balanceOf(address(this)) /* 6-dec */ + _gmValueInUsdc($) /* 18-dec */;
}
```

Every conversion consumes this corrupted TVL:

```solidity
function _convertToShares(uint256 assets) internal view returns (uint256 shares) {
    ...
    return (assets * totalShares) / totalAssets_;   // totalAssets_ inflated 1e12x once GM held
}
function _convertToAssets(uint256 shares) internal view returns (uint256 assets) {
    return (shares * _totalValueLocked()) / totalSupply();
}
```

## Impact

Once a pool deploy executes:
- `totalAssets()` jumps ~**1e12×** for the same real value.
- A user who deposits while GM is held is minted **~1e12× too few shares** (`assets * totalShares / inflatedTVL`), so their stake in the vault is negligible.
- Their `release()` payout (`shares * TVL / totalSupply`) rounds to **0** and the call reverts `InsufficientVaultBalance` — they cannot recover any of their principal.
- Holders minted **before** the deploy (at the correct 1e12 rate) hold ~1e12× more shares and can withdraw essentially the **entire** vault, including the new depositor's funds.

Net effect: **permissionless, deterministic loss of depositor principal**, plus a fully corrupted share price for the protocol.

> Why the test suite missed it: the repo's `MockExchangeRouter` mints GM **1:1 with the 6-decimal USDC amount** (`CarthaVaultPool.t.sol`: "100_000e6 USDC -> 100_000e6 GM") instead of the realistic 18-decimal amount. That second error cancels the 1e30 price, so `deployedGmBalance() == gmBal` passes. `test_Control_6DecMintNoInflation()` reproduces the masking.

## Step-by-step (from the PoC)

1. `user1` deposits 100,000 USDC → minted `100_000e6 * 1e12 = 1e23` shares (correct rate).
2. Keeper `deployToPool(100k)`; the 0xM keeper executes → vault holds `100_000e18` GM (realistic GMX: 18-dec GM at $1).
3. `totalValueLocked()` now reports `100_000e18` (= `1e23`) for $100k of real value → **exactly 1e12× inflated** (asserted).
4. `user2` deposits 100,000 USDC → minted only `~1e11` shares (≈1e12× fewer).
5. Keeper recalls GM → 200k USDC now idle, TVL correct again.
6. `user2.release()` **reverts** `InsufficientVaultBalance` (payout rounds to 0) — recovers **$0**.
7. `user1.release()` withdraws **199,999.99 USDC** — nearly both deposits.

```
True value (USDC, 6dec): 100000000000
Reported TVL          : 100000000000000000000000   <-- 1e12x inflation
user2 deposited (USDC): 100000000000  recovered: 0 (release reverts)
user1 deposited (USDC): 100000000000  recovered: 199999999999
```

## Recommended fix

Normalize the GM leg to the asset's decimals before summing. Either return 6-decimal USDC from `gmValueInUsdc` (divide by an extra `10^(18 - assetDecimals)`), or scale the GM term inside `_totalValueLocked`:

```solidity
// gmValueInUsdc currently returns an 18-dec USD value; convert to the 6-dec asset scale:
uint256 gmInAsset = gmValueRaw / (10 ** (18 - IERC20Metadata($.asset).decimals()));
return IERC20($.asset).balanceOf(address(this)) + gmInAsset;
```

Also fix the test harness so the mock mints GM at the real 18-decimal magnitude, and add an invariant test that a deploy → settle round-trip leaves `totalValueLocked()` unchanged (±rounding).

## Re-verification note

Re-verified end-to-end with the project's own Foundry harness, modeling GMX faithfully: GM token = 18 decimals; `MockExchangeRouter.setGmPrice(1, 1e12)` mints the realistic `100_000e18` GM for 100k USDC (and round-trips back to 100k USDC on withdrawal); `Mock0xMReader.setMarketTokenPrice(1e30)` = $1/GM. **All four PoC tests pass**, including `test_RealReaderPriceScale_Is1e30PerWholeToken`, which proves the `1e30`-per-whole-token scale by replaying the real `MarketUtils.getMarketTokenPrice` formula (`WEI_PRECISION × poolValue / supply`) rather than taking the mock price on faith — closing the "is the reader price really 1e30?" gap.

> Note on a live read: 0xMarkets is reviewed here as a **pre-deploy** fork, so there is no mainnet `Reader` to fork-read against. The scale is instead proven from the in-scope source (`MarketUtils.sol:156-163`, `Precision.sol`) and reproduced numerically in the PoC. If/when 0xMarkets is deployed, a one-line read of `Reader.getMarketTokenPrice(...)` on a live $1-ish GM market will return a value on the `~1e30` scale, confirming the same.
