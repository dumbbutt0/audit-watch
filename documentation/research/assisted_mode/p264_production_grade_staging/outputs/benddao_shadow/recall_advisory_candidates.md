# Recall-First Harness — SHADOW advisory (benddao)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=17 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | LiquidationLogic._repayUserERC20Debt | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | LiquidationLogic.executeCrossLiquidateERC721 | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | GenericLogic.calculateUserAccountDataForLiquidate | T1,T7,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | InterestLogic.updateInterestIndexs | T6 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | ValidateLogic.validateDepositERC721 | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | ValidateLogic.validateWithdrawERC721 | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | YieldStakingBase.batchStake | T5 | top_n_overall | NEEDS_RANKING |
| 7.0 | LiquidationLogic._calculateDebtAmountFromERC721Collateral | T1,T7,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | LiquidationLogic.viewGetUserCrossLiquidateData | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | CrossLiquidation.crossLiquidateERC20 | T1,T5,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | YieldStakingBase.batchUnstake | T2,T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | YieldStakingBase.batchRepay | T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 12.0 | GenericLogic.calculateUserAccountData | T7,T9 | t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | LiquidationLogic.executeCrossLiquidateERC20 | T1,T7 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | IsolateLogic.executeIsolateLiquidate | T1,T7 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
