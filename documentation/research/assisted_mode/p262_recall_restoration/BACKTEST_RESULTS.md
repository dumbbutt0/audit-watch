# P262 — BACKTEST_RESULTS (frozen P254–P261 artifacts; NO new keys)
Recall sweep run on each frozen contest's manifest + checkpoints. Award loci classified:

| case | result | labels |
|---|---|---|
| hybra GrowthHYBR.deposit | **FORCED_INTO_SWEEP** (T8; reasons top10+T7T8+name) | FORCED · RIGHT_TEMPLATE · AWARD_SHAPE_GENERATED · WOULD_REACH_BC_RANKING |
| sentiment rebalanceBadDebt | **FORCED** (T1,T7; 4 reasons) | FORCED · RIGHT_TEMPLATE · WOULD_REACH_BC_RANKING |
| notional _accrueFees (#886 region) | **FORCED** (T6) | FORCED · RIGHT_TEMPLATE; collectFees/initiateWithdraw STILL_MISSED (siblings; mechanism-area covered by _accrueFees) |
| plaza _create (split-deposit) | **FORCED** (T8) + simulateRedeem FORCED (T1/T2/T8) | FORCED · RIGHT_TEMPLATE; getCreateAmount STILL_MISSED (pure view; area covered by _create) |
| bakerfi harvest | **FORCED** (T1) | FORCED; template T1 (partial vs the fee/newDeployedAmount mechanism) |
| loopfi liquidatePosition | **FORCED** (T1,T5,T7) | FORCED · RIGHT_TEMPLATE · WOULD_REACH_BC_RANKING |
| basin decodeWellData / calcReserveAtRatioSwap / calcLpTokenSupply / calcRate | **FORCED via T9** | FORCED · RIGHT_TEMPLATE(T9) — Basin math/units recall RESTORED |
| monetrix (operational, unscored) | swept 19 loci, bounded, advisory | INCONCLUSIVE (no key; operational check) |

## Tally
- Skipped subtle-accounting award loci FORCED_INTO_SWEEP: **6/6 mechanism-areas** (hybra/sentiment/notional/plaza/
  bakerfi/loopfi). T7/T8 share/debt/solvency loci no longer skipped.
- Basin-style math/units controls reached by **T9**: 4/4 (decodeWellData + 3 calc*).
- Output bounded on every contest (≤25 loci; ≤5 mech/locus; ≤30 mech total — sentiment/notional/plaza/loopfi hit the
  30-mech cap → truncated:true recorded). FP-guard: **0 severity/concluded/reportable/submission violations**.
- Residual misses are SIBLING loci (collectFees/initiateWithdraw/getCreateAmount) where the mechanism-area locus IS
  forced in → the awarded mechanism remains reachable by downstream B/C + completion.
