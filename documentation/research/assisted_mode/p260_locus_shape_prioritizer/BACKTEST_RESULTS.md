# P260 — BACKTEST_RESULTS (frozen P254–P259 artifacts; NO new answer keys)
Module receives manifest + checkpoint JSON only; award loci (known from prior reveals) used ONLY to score its blind
top-15 ranking. The 7 required backtest questions:

| # | question | result | labels |
|---|---|---|---|
| 1 | LoopFi CDPVault.liquidatePosition? | **rank #13/15, T7, APPLY_RANKING** | WOULD_PRIORITIZE_AWARD_LOCUS · WOULD_APPLY_RIGHT_TEMPLATE · WOULD_FEED_BC_RANKING |
| 2 | Basin decodeWellData + calcReserveAtRatio? | **NOT prioritized** (basin yields only 3 candidate loci; math/units functions have no routed template) | STILL_MISSES_LOCUS (shape-vocabulary gap: math/units/convergence class) |
| 3 | BakerFi harvest (fee/newDeployedAmount)? | **rank #5, T1** | WOULD_PRIORITIZE_AWARD_LOCUS · STILL_WRONG_SHAPE (T1 external-dep, not the T6/fee mechanism) |
| 4 | Plaza runner-up regions (P256)? | **Pool._create #2 (T8), create #6, simulateCreate #15** | WOULD_PRIORITIZE_AWARD_LOCUS · WOULD_APPLY_RIGHT_TEMPLATE · WOULD_FEED_BC_RANKING |
| 5 | Notional N-L2 fee accrual? | **_accrueFees #14 (T6)**; collectFees/initiateWithdraw missed | WOULD_PRIORITIZE_AWARD_LOCUS (partial) · WOULD_APPLY_RIGHT_TEMPLATE |
| 6 | Hybra GrowthHYBR.deposit (P259 skipped locus)? | **rank #1, T8, APPLY_RANKING** | WOULD_PRIORITIZE_AWARD_LOCUS · WOULD_APPLY_RIGHT_TEMPLATE · WOULD_GENERATE_AWARD_SHAPE · WOULD_FEED_BC_RANKING |
| 7 | Sentiment bad-debt at correct locus (not wrong locus)? | **Pool.rebalanceBadDebt #6, T7** (correct locus, unlike P259 placement) | WOULD_PRIORITIZE_AWARD_LOCUS · WOULD_APPLY_RIGHT_TEMPLATE · WOULD_FEED_BC_RANKING |

## Tally
- Award locus prioritized into top-15: **6/7** (miss = basin math/units class).
- Right template routed: 5/7 (hybra/plaza/sentiment/loopfi/notional); partial bakerfi (T1 vs fee); miss basin.
- **Core P259 fix CONFIRMED:** hybra GrowthHYBR.deposit (the skipped checkpoint-hit award locus) → **#1 with T8**;
  sentiment bad-debt placed at the **correct locus** (P259's wrong-locus error fixed).
- Output bounded (top-15), top loci are plausible high-risk functions (deposit/withdraw/liquidate/_create/
  multiSplit/rebalance) — **no noise flood**.
- Zero production changes; no answer key used by the module.

## Honest caveats
Backtest is necessary, NOT sufficient (it scores against loci the module's own signal-set tends to surface; the
real proof is a fresh-contest run, P261). basin's award class (units/decimals/convergence math) is **not modeled**
by the 8 accounting/state shape templates → a known coverage gap. bakerfi template was T1 not the exact fee
mechanism. notional fee partial (1/3 loci). loopfi liquidatePosition ranked low (#13) — present but not top.
