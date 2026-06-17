# Cartha C-1 — cross-protocol reachability CONFIRMED (via 0xMarkets source)

Cartha **C-1** (stale/zero-TVL share mispricing → PnL theft) depends on the precondition that 0xMarkets'
`getMarketTokenPrice(...)` can return **≤ 0** (so `Cartha PoolDeployLib.gmValueInUsdc` returns 0 → Cartha
`_totalValueLocked()` reads 0 while real GM value exists → the first-deposit-rate mint fires). At the time of the
Cartha report this was rated *conditional* (Medium→High) pending confirmation of 0xM behavior.

**Confirmed from 0xMarkets source** (`0xMarkets_contract-main` @ `e94daee…`, `contracts/market/MarketUtils.sol`):

```solidity
function getMarketTokenPrice(...) external view returns (int256, MarketPoolValueInfo.Props memory) {
    ...
    if (supply == 0) { return (Precision.FLOAT_PRECISION.toInt256(), poolValueInfo); }
    if (poolValueInfo.poolValue == 0) { return (0, poolValueInfo); }        // returns 0
    int256 marketTokenPrice = Precision.mulDiv(Precision.WEI_PRECISION, poolValueInfo.poolValue, supply);
    return (marketTokenPrice, poolValueInfo);                                // negative if poolValue < 0
}
```

- `poolValue` is `int256` and can be **0 or negative**: `poolValue = long+short pool USD (± impact pool) − capped
  pending trader PnL`. When traders are deeply in profit relative to pool token value (the `MAX_PNL_FACTOR_*` path),
  `poolValue ≤ 0`.
- Cartha requests the price with `MAX_PNL_FACTOR_FOR_DEPOSITS` and `maximize = false` (**minimize** the pool value),
  which makes the `≤ 0` read **more** likely, not less.

**Conclusion:** the `gmPrice ≤ 0` precondition for Cartha C-1 is a **real, market-induced protocol state** (deeply-in-
profit traders / stressed pool), not a misconfiguration or an oracle bug. Combined with Cartha deploying a child's
idle USDC into the pool (idle ≈ 0), Cartha's TVL can read 0 with real GM value present, and a permissionless
`depositAndLock` mints at the stale first-deposit rate. **Cartha C-1's realistic severity should be raised toward
High.** (This is GMX-inherited 0xM behavior — not itself a 0xMarkets bug; see `reports/0xmarkets-2026-06-13/
FINDINGS.md` X-1.)
