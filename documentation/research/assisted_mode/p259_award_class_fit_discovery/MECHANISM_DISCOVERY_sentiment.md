# sentiment — Phase 3: Two-pass mechanism discovery (PRE-REVEAL, FROZEN) — CONTAMINATED-DISCLOSED
Pass 1 = 7 families. Pass 2 = 8 templates. #541/max* excluded. Discovery only.
## S-L1 liquidate/_transferAssetsToLiquidator
**Pass 1:** M1 (A) seize>repay accounting; M2 (F) liquidator vs position owner identity; M3 (B) collateral pricing convexity.
**Pass 2:** T7 liquidation/solvency-boundary: liquidate a position just over/under health → seize disproportionate
collateral / leave bad debt (NEW framing); T8 share-price: collateral valued via pool share price manipulable;
T2 redemption-coupling: seizure alters position state used later.
## S-L2 rebalanceBadDebt
**Pass 1:** M1 (A) bad-debt socialization double-count; M2 (C) state after writedown.
**Pass 2:** T7 solvency-boundary: who is solvent after rebalance; T1 external-dependency: oracle drives bad-debt;
T6 cross-tx: rebalance timing vs deposit/withdraw (NEW).
## S-L3 reorder queues
**Pass 1:** M1 (C) queue order changes allocation; M2 (A) accounting per pool.
**Pass 2:** T2 withdrawal-state-coupling: reorder withdraw queue to strand/redirect withdrawals (NEW); T5 liveness:
reorder bricks withdrawal.
**FREEZE.** Pass 2 added: S-L1 T7 solvency-boundary, S-L2 T6 cross-tx, S-L3 T2 withdrawal-coupling.
