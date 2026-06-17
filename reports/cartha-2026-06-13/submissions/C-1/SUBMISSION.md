<!--
PLATFORM-PASTE-READY version of the Cartha C-1 report. Plain prose + standard code fences only — no blockquote
header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the matching field. Facts
are identical to report.md (validated, PoC passing). Copy from the RAW file, not a rendered preview.

NOTE: Cartha was supplied as a dropped zip (commit 4c51f2a), not a known bounty URL — confirm the correct
Target/program before submitting.
-->

# Field: Target
Cartha Vaults (Bittensor SN35 liquidity vaults over 0xMarkets GM pools) — commit 4c51f2a
(repo supplied as an archive; confirm the official submission target/URL before submitting)

# Field: Category
Business Logic Errors

# Field: Severity
High

# Field: Title
Zero-TVL fallback lets a depositor mint at the first-deposit rate and steal existing holders' accrued PnL

# Field: Vulnerability details

`CarthaVault._convertToShares` falls back to the first-deposit rate (the 1e12 decimal offset) whenever TVL
reads zero — even when `totalSupply > 0`. TVL is `idle USDC + GM value`, and the GM value returns 0 whenever
the 0xMarkets market-token price is `<= 0`. So when a child's idle USDC is deployed (idle ~ 0) and the 0xM
oracle reports `gmPrice <= 0` while real, profitable GM value still exists, TVL reads 0 and a permissionless
`depositAndLock` mints at the stale 1e12 rate instead of the live (higher) price. The over-minted shares are a
claim on existing holders' accrued PnL.

This is High because it is direct, permissionless theft of other depositors' funds (their accrued PnL) — no
privileged role is needed, and the `gmPrice <= 0` precondition is confirmed reachable (see Reachability below).

## Root cause

```solidity
// CarthaVault._convertToShares
uint256 totalShares = totalSupply();
uint256 totalAssets_ = _totalValueLocked();              // idle USDC + GM value
if (totalShares == 0 || totalAssets_ == 0) {             // TVL==0 treated as a brand-new vault
    return assets * 10 ** (decimals() - IERC20Metadata($.asset).decimals());   // 1e12 offset
}
return (assets * totalShares) / totalAssets_;            // correct live-price branch
```

`_totalValueLocked = idle + PoolDeployLib.gmValueInUsdc(...)`, and `gmValueInUsdc` returns 0 when the 0xM
market-token price is `<= 0`:

```solidity
// PoolDeployLib.gmValueInUsdc
int256 gmPrice = _getGmPrice(reader, dataStore, market, oracle);
if (gmPrice <= 0) return 0;
```

So `totalAssets_ == 0` while `totalSupply > 0` and real value exists — and the brand-new-vault branch fires,
minting at the first-deposit rate.

## Reachability (why gmPrice <= 0 is real)

GMX-style market-token price is a signed `int256`: `MarketUtils.getMarketTokenPrice` returns 0 when
`poolValue == 0` and negative when `poolValue < 0` (deeply trader-profitable pools past
`MAX_PNL_FACTOR_FOR_DEPOSITS` — the exact factor `_getGmPrice` requests), and Cartha queries with
`maximize = false` (minimize), which makes the `<= 0` read more likely. The project itself treats this as a
real scenario: `test/vault/CarthaVaultPool.t.sol::test_TVL_HandlesNegativeGmPrice`. (Cross-confirmed by
auditing 0xMarkets directly — finding X-1.)

## Impact

Permissionless theft of existing depositors' accrued PnL during a zero-TVL read. In the PoC: a 100k position
grown to 150k (GM value, idle drained), oracle reads `gmPrice = 0` so TVL reads 0; the attacker
`depositAndLock(100k)` mints at the first-deposit rate; after the price recovers the attacker claims 125k for a
100k deposit, and the victim goes 150k -> 125k (25k stolen).

## Suggested fix

Do not fall back to the first-deposit rate when `totalSupply > 0`: if `totalSupply > 0 && totalAssets_ == 0`,
revert (or pause minting). Treat a `<= 0` / stale GM price as a hard error for mint/redeem pricing (revert),
not as `TVL += 0`. Add a deposit `minSharesOut` and an oracle-freshness check.

# Field: Validation steps

The PoC runs against the project's own contracts in a local Foundry harness; it passes. From the harness root:

```bash
forge test --match-contract PoC_StaleTvlMint -vv
```

Captured output (passes):

```
[PASS] test_PoC_staleTvlZeroRead_stealsPnL()
  attacker deposited (USDC): 100000
  attacker claim       (USDC): 125000
  victim before        (USDC): 150000
  victim after         (USDC): 125000
Suite result: ok. 1 passed; 0 failed; 0 skipped
```

# Field: Attachments
- PoC_StaleTvlMint.t.sol
- poc_output.log   (captured passing run)
