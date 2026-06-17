# 0xMarkets (GMX Synthetics fork) — audit findings

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Source: user-provided `0xMarkets_contract-main.zip` → `/tmp/0xm-hunt/0xMarkets_contract-main/` (commit `e94daee…`).
Target: **0xMarkets = a GMX Synthetics fork/rebrand** (README is GMX's verbatim; repo ships the GMX ABDK/Certora/
Dedaub/12× Guardian audit PDFs). 238 `.sol`. The GMX core is treated as audited; the hunt focuses on the
**0xMarkets-specific delta** and on a **cross-protocol confirmation for the Cartha audit**.

## Scope decision
Re-auditing vanilla GMX Synthetics (10+ shipped audits) is infeasible and low-value. The 0xMarkets delta vs stock GMX
is the **insurance-fund module** (`contracts/insurance/`, not present in stock GMX) wired into the position-close path
(`DecreasePositionCollateralUtils`), plus `contributor/`, and Pyth-oracle/config rebrand wiring. This report covers
that delta + the Cartha cross-protocol question. The GMX core (orders/positions/swaps/ADL/liquidation/oracle) was not
re-audited — assumed audited-sound.

---

## X-1 (cross-protocol) — CONFIRMS Cartha C-1: `getMarketTokenPrice` can return ≤ 0
**File:** `contracts/market/MarketUtils.sol :: getMarketTokenPrice`.

```solidity
if (supply == 0) { return (Precision.FLOAT_PRECISION.toInt256(), poolValueInfo); }  // 1 USD
if (poolValueInfo.poolValue == 0) { return (0, poolValueInfo); }                    // <-- returns 0
int256 marketTokenPrice = Precision.mulDiv(Precision.WEI_PRECISION, poolValueInfo.poolValue, supply); // signed
return (marketTokenPrice, poolValueInfo);                                            // <-- negative if poolValue < 0
```

`poolValue` is an `int256` (from `getPoolValueInfo`) and can be **0 or negative** — `poolValue = long+short pool USD
(± impact) − capped pending trader PnL`, which goes ≤ 0 when traders are deeply in profit relative to pool token value
(the `MAX_PNL_FACTOR_*` cap path). So `getMarketTokenPrice` legitimately returns `≤ 0`. **Cartha** (`reports/
cartha-2026-06-13/`) calls this with `MAX_PNL_FACTOR_FOR_DEPOSITS` + `maximize = false` (minimize), which makes the
≤ 0 read *more* likely, and `Cartha PoolDeployLib.gmValueInUsdc` then returns 0 → Cartha `_totalValueLocked()` reads
0 → the Cartha C-1 first-deposit-rate mint bug fires. **This confirms Cartha C-1's precondition is a real protocol
state, not a misconfiguration — its realistic severity should be raised toward High.** (See
`cartha-C1-reachability.md`.) This is GMX-inherited behavior, not a 0xMarkets bug — it is reported here only to ground
the Cartha finding.

---

## I-1 (Medium, design) — Insurance injection compensates *current* LP holders, not drawdown-era holders (JIT capture)
**Files:** `contracts/insurance/InsuranceFundUtils.sol :: attemptInjectPool` / `getDrawdownFraction`; called from
`DecreasePositionCollateralUtils.processCollateral`.

When realized pool drawdown (live pool USD vs the epoch snapshot) exceeds the per-market trigger, the fund transfers
reserve into `MarketToken` and credits the pool via `applyDeltaToPoolAmount`, raising the market-token price for
**whoever holds LP at injection time**. The reserve was funded by liquidation-fee slices contributed over the epoch,
intended to compensate LPs who bore the drawdown. Because the compensation lands on the pool (not on a per-LP
snapshot), an LP who deposits *after* the drawdown (and before/at injection) captures a pro-rata share of the
injected reserve they never lost. GMX deposits/withdrawals are async + fee'd (limiting pure JIT), but the
compensation-to-current-holders mismatch is a real value-distribution flaw. Hard to PoC standalone (needs the full
GMX deposit/withdrawal/keeper machinery). **Fix:** gate injection eligibility / track drawdown per share-epoch, or
restrict deposits while a market is in a drawdown-injection state.

## I-2 (Low, config footgun) — `triggerFactor` default of 0 means "inject on any drawdown"
**File:** `InsuranceFundUtils.attemptInjectPool` (line ~196-205).
The "off" sentinel is `type(uint256).max`; the **unset DataStore default is 0**, which means *inject on any drawdown
> 0*. A market that has collected insurance fees (non-zero reserve) but whose `insuranceFundDrawdownTriggerFactor`
was never explicitly set to `type(uint256).max` will drain its reserve into the pool on the slightest realized
drawdown. The code comment flags this as a deploy-script responsibility, but the safe default is inverted. **Fix:**
treat unset (0) as disabled, or require explicit enablement.

---

## Reviewed & sound (custom delta)
- **`InsuranceVault`** = stock GMX `StrictBank`; `transferOut` is `onlyController`-gated → custody safe; no custom
  withdrawal path.
- **Collection (`InsuranceFundUtils.deposit`)** conserves: the insurance slice is *subtracted from* `feeAmountForPool`
  in `PositionPricingUtils.getPositionFees` (line 351, `… − liquidationFeeAmountForInsurance`), and it is only a slice
  of the **liquidation** fee — so physically moving it to the vault does not over-state `poolAmount`. No double-count.
- **Injection** conserves: `vault.transferOut(pnlToken, marketToken, injected)` + `applyDeltaToPoolAmount(+injected)`
  + reserve bucket `−injected` — physical and accounting move together; bounded by reserve and by `missingUsd`.
- **`SettlementHandler.snapshotEpoch`** is `onlyOrderKeeper` + `globalNonReentrant` + epoch-length-idempotent (can't
  be rewritten mid-epoch to reset drawdown). Snapshot and live drawdown use the same `getPoolValueExcludingUnrealized
  Pnl(..., false)` pick rule (internally consistent).
- Library external functions run in the controller handler's context (delegatecall) → bank role-gating holds.

## Bottom line
0xMarkets is GMX Synthetics; the custom insurance-fund delta is conservation- and access-sound, with two design/config
notes (I-1 Medium JIT-capture, I-2 Low default footgun) and no clean Critical. The most valuable result is **X-1**:
the source confirms 0xMarkets' `getMarketTokenPrice` can return ≤ 0, which **validates Cartha C-1's reachability** and
raises its realistic severity. GMX core not re-audited (audited-sound). **Nothing submitted.**
