# P263 — SELECTED_LOCI (from recall-sweep output; PRE-REVEAL) — 3/4 are RECALL-DELTA
- **SL1 YieldStakingBase.batchUnstake / YieldSavingsDai.batchUnstakeAndRepay (RECALL-DELTA; T2/T5)** — yield-
  staking unstake+repay loop; distinct subsystem the narrow liquidation-focused top-5 skips. no-hindsight lock:
  forced by checkpoint_hit_name_keyword; base/narrow would skip; incomplete=unstake/repay state-coupling/solvency.
- **SL2 InterestLogic._accrueFeeToTreasury (RECALL-DELTA; T6)** — protocol fee accrual via prevGroupBorrowIndex;
  classic index/fee drift. forced by checkpoint_hit_evidence_marker; narrow skips (only updateInterestIndexs in top5).
- **SL3 CrossLiquidation.crossLiquidateERC20 (RECALL-DELTA; T1/T5/T7)** — cross-collateral liquidation + native-
  token handling + borrower/msgSender/asset identity. forced by 4 reasons; outside narrow top-5.
- **SL4 LiquidationLogic._repayUserERC20Debt (narrow-baseline #1; T7)** — contrast/coverage (would be selected anyway).
no-hindsight: selected pre-reveal from the sweep; ≥1 forced-in-outside-narrow satisfied (SL1/SL2/SL3). FREEZE.
