# C-1 (High) — Stale/zero-TVL share mispricing lets a depositor steal existing holders' PnL

- **Target:** Cartha Vaults (Bittensor SN35 vaults over 0xMarkets GM pools), commit `4c51f2a…`.
- **Vulnerable files (copied in `vulnerable/`):** `src/CarthaVault.sol` (`_convertToShares`, `_totalValueLocked`),
  `src/libraries/PoolDeployLib.sol` (`gmValueInUsdc`). Same shape in `CarthaParentVault._convertToShares`.
- **Severity:** **High** — direct theft of accrued PnL. The `gmPrice ≤ 0` precondition is **confirmed reachable** by
  auditing 0xMarkets itself: `MarketUtils.getMarketTokenPrice` returns `0` when `poolValue == 0` and **negative** when
  `poolValue < 0` (signed `int256` pool value, ≤ 0 when traders are deeply in profit), and Cartha queries it with
  `maximize=false` (minimize), which makes the ≤ 0 read *more* likely. See `../../cartha-C1-reachability.md` and
  `reports/0xmarkets-2026-06-13/FINDINGS.md` (X-1).
- **PoC:** `poc/PoC_StaleTvlMint.t.sol` (passing) · log `poc_output.log`.
- **Attacker:** permissionless (`depositAndLock`).

## Root cause
Share minting falls back to the **first-deposit rate (1e12 decimal offset)** whenever TVL reads zero — *even when
`totalSupply > 0`*:

```solidity
// CarthaVault._convertToShares
uint256 totalShares = totalSupply();
uint256 totalAssets_ = _totalValueLocked();              // idle USDC + GM value
if (totalShares == 0 || totalAssets_ == 0) {             // <-- TVL==0 treated as a brand-new vault
    return assets * 10 ** (decimals() - IERC20Metadata($.asset).decimals());   // 1e12 offset
}
return (assets * totalShares) / totalAssets_;            // correct live-price branch
```

`_totalValueLocked = idle + PoolDeployLib.gmValueInUsdc(...)`, and `gmValueInUsdc` **returns 0 when the 0xM market
token price is `≤ 0`**:

```solidity
// PoolDeployLib.gmValueInUsdc
int256 gmPrice = _getGmPrice(reader, dataStore, market, oracle);
if (gmPrice <= 0) return 0;
```

So when a child's idle USDC is deployed (idle ≈ 0) and the 0xM oracle reports `gmPrice ≤ 0`, `_totalValueLocked()`
reads **0 while real, profitable GM value still exists**, and any permissionless `depositAndLock` mints at the stale
1e12 first-deposit rate instead of the live (higher) price. The over-minted shares are a claim on existing holders'
PnL.

The project treats `gmPrice ≤ 0` as a real scenario — `test/vault/CarthaVaultPool.t.sol::test_TVL_HandlesNegativeGmPrice`.
GMX-style market token price can go negative when cumulative trader PnL exceeds the pool's `MAX_PNL_FACTOR_FOR_DEPOSITS`
— the exact factor `_getGmPrice` requests.

## Impact
Permissionless theft of existing depositors' accrued PnL during a zero-TVL read. PoC: a 100k position grown to 150k
(GM value, idle drained); oracle reads `gmPrice = 0` → TVL reads 0; attacker `depositAndLock(100k)` mints at the
first-deposit rate; after the price recovers the attacker can claim **125k for a 100k deposit**, victim **150k → 125k
(25k stolen)**.

## PoC (passing)
`forge test --match-contract PoC_StaleTvlMint -vv` (from `../../harness/`). Logs: attacker deposited 100k → claim
125k; victim 150k → 125k.

## Fix
Do **not** fall back to the first-deposit rate when `totalSupply > 0`: if `totalSupply > 0 && totalAssets_ == 0`,
revert (or pause minting). Treat a `≤ 0` / stale GM price as a hard error for mint/redeem pricing (revert), not as
`TVL += 0`. Add a deposit `minSharesOut` and an oracle-freshness check.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Business Logic Errors (ERC-4626 share mispricing: `_convertToShares` falls back to the first-deposit 1e12 rate when `_totalValueLocked()` reads 0 while `totalSupply>0` and value exists → deposit at a stale rate steals existing holders' value)
- **Secondary category:** Blockchain → Transaction-Ordering Dependence (TOD) / Front Running (JIT deposit timed to the zero-TVL window)
- **CWE (informative):** CWE-682 (Incorrect Calculation); CWE-840 (Business Logic Errors)

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Stale/zero-TVL share theft | `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N` | **6.8** | Medium |

> S:C — the loss accrues to *other* vault holders (beyond the attacker's own position). AC:H — requires the gmPrice<=0 / TVL==0 window (reachability confirmed via 0xMarkets X-1). CVSS band (Medium) is conservative; the protocol/bounty severity is **High** because it is direct, permissionless theft of other users' funds once that window is reached.

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
