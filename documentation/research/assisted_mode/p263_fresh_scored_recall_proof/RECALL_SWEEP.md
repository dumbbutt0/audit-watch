# P263 — RECALL_SWEEP (frozen P262; PRE-REVEAL) — the core measurement
Recall sweep forced shape discovery on **17 loci** (bounded; 30 mechs; truncated:true), of which **12 are
RECALL-DELTA** (outside the narrow top-5 baseline = loci the old pre-P262 narrow path would have SKIPPED):
- YieldStakingBase.batchUnstake (T2,T5) · batchRepay (T5) · batchStake (T5)  [entire yield subsystem narrow path skips]
- InterestLogic._accrueFeeToTreasury (T6)  [fee-to-treasury accrual]
- CrossLiquidation.crossLiquidateERC20 (T1,T5,T7) · LiquidationLogic.executeCrossLiquidateERC20 (T1,T7) ·
  _calculateDebtAmountFromERC721Collateral (T1,T7,T9) · viewGetUserCrossLiquidateData (T1,T7)
- GenericLogic.calculateUserAccountData (T7,T9) · ValidateLogic.validateWithdrawERC721 (T2) ·
  validateCrossLiquidateERC721 (T1,T7) · IsolateLogic.executeIsolateLiquidate (T1,T7)
T9 fired on calc*/debt-amount math loci (GenericLogic, _calculateDebtAmountFromERC721Collateral). FP-guard: all
RECALL_CANDIDATE_ONLY, 0 severity/concluded. Full JSON: outputs/benddao_recall_sweep.json.
**Recall delta = 12 loci forced in beyond narrow top-5.** Whether any AWARDED locus is among them → reveal.
