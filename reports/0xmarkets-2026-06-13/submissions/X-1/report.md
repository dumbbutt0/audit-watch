# X-1 (cross-protocol confirmation) — `getMarketTokenPrice` can return ≤ 0

- **Target:** 0xMarkets (GMX Synthetics fork), commit `e94daee…`.
- **Vulnerable file (copied in `vulnerable/`):** `contracts/market/MarketUtils.sol` (`getMarketTokenPrice`).
- **Severity:** Informational *for 0xMarkets* (GMX-inherited, by design) — but it **confirms the precondition for
  Cartha C-1 (High)**.
- **Proof type:** source-confirmed (no runnable PoC — a full GMX build is required to drive `getPoolValueInfo`).

## Fact
```solidity
// MarketUtils.getMarketTokenPrice
if (supply == 0) { return (Precision.FLOAT_PRECISION.toInt256(), poolValueInfo); }   // 1 USD
if (poolValueInfo.poolValue == 0) { return (0, poolValueInfo); }                      // returns 0
int256 marketTokenPrice = Precision.mulDiv(Precision.WEI_PRECISION, poolValueInfo.poolValue, supply); // signed
return (marketTokenPrice, poolValueInfo);                                             // negative if poolValue < 0
```
`poolValue` is a signed `int256` (`pool USD ± impact − capped pending trader PnL`). It is **0 or negative** when
capped pending trader PnL meets/exceeds pool token value (deeply-in-profit traders / `MAX_PNL_FACTOR_*` path). So
`getMarketTokenPrice` legitimately returns `≤ 0`.

## Why it matters (cross-protocol)
**Cartha** (`reports/cartha-2026-06-13/`) reads this price via `PoolDeployLib.gmValueInUsdc`, which maps `gmPrice ≤ 0`
to `0`, making Cartha `_totalValueLocked()` read 0 while real GM value exists → Cartha C-1's first-deposit-rate mint
fires. Cartha queries with `maximize = false` (minimize), which makes the `≤ 0` read *more* likely. This confirms
Cartha C-1 is reachable as a real market state (not a misconfiguration) → C-1 rated **High**. See
`../../cartha-2026-06-13/cartha-C1-reachability.md`.

## Note
This is GMX-inherited behavior, **not a 0xMarkets bug** — recorded only to ground the Cartha finding. No 0xMarkets fix
is implied; the fix belongs in integrators (treat `≤ 0` GM price as an error, not `TVL += 0`).

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Business Logic Errors (signed `getMarketTokenPrice` can return ≤ 0 by design — int256, 0 when poolValue==0, negative when poolValue<0)
- **CWE (informative):** CWE-682 (Incorrect Calculation) — informative

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| GMX-inherited signed price ≤ 0 | `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:N` | **0.0** | None |

> Informational for 0xMarkets (inherited GMX-Synthetics behaviour, not a 0xM-introduced bug). No standalone impact here — recorded because it grounds the reachability of **Cartha C-1**. CVSS base 0.0 (no direct impact in 0xM scope).

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
