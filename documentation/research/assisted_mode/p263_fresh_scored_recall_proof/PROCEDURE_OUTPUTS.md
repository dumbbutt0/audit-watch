# P263 — PROCEDURE_OUTPUTS (five ops on B/C winners; PRE-REVEAL)
## SL1 batchUnstake: STS PASS (unstake then repay loop) · AAS PARTIAL · TSE CANDIDATE_STRENGTHENED (partial-fill
strands NFT/position) · IDC PARTIAL (yield/share accounting on unstake) · CCIT NO_EFFECT → PARTIAL_CHAIN (hypothesis).
## SL2 _accrueFeeToTreasury: STS PASS · IDC CANDIDATE_STRENGTHENED (fee on stale prevGroupBorrowIndex → treasury
over/under-accrual) · TSE PARTIAL → PARTIAL_CHAIN (hypothesis).
## SL3 crossLiquidateERC20: STS PASS · AAS PASS (liquidator chooses debtToCover/collateral) · IDC CANDIDATE_STRENGTHENED
(seize vs debt boundary) · CCIT CANDIDATE_STRENGTHENED (borrower vs msgSender vs asset) · TSE PASS → PARTIAL_CHAIN (hypothesis).
## SL4 _repayUserERC20Debt: STS PASS · IDC PARTIAL → PARTIAL_CHAIN (hypothesis).
ALL UNSCORED pre-reveal (hypotheses; advisory). FREEZE before key opened.
