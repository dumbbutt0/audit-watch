# P263 — RANKING_OUTPUTS (Profile B / Profile C on sweep mechanisms; PRE-REVEAL)
## SL1 batchUnstake (T2/T5)
- B winner: T2 withdrawal-state-coupling (unstake alters yield/share state affecting later repay/solvency); C winner:
  T5 liveness (unstake/repay loop partial-failure strands a position); top-2 {T2,T5}. falsifier: unstake+repay atomic & fully reverts on failure.
## SL2 _accrueFeeToTreasury (T6)
- B winner: T6 cross-tx index drift (fee accrued on prevGroupBorrowIndex vs current → over/under-accrual to treasury);
  C winner: T6 (same); top-2 {T6}. falsifier: fee uses the exact up-to-date index.
## SL3 crossLiquidateERC20 (T1/T5/T7)
- B winner: T7 solvency-boundary (cross-liquidation seize vs debt-cover boundary; native-token wrap); C winner: T1
  external-dep / CCIT (borrower vs msgSender vs collateral/debt asset); top-2 {T7,T1}. B≠C. falsifier: seize bounded by health & repaid debt.
## SL4 _repayUserERC20Debt (T7)
- B winner: T7 repay-accounting; C winner: T1; top-2 {T7,T1}.
FREEZE.
