# P262 recall-first sweep — benddao_coverage_manifest (ADVISORY ONLY; no severity/conclusions)

swept_loci=17 · total_mechs_to_ranking=30 · truncated=True

| p260_rank | locus | templates | inclusion | #mechs | status |
|---|---|---|---|---|---|
| 0 | LiquidationLogic._repayUserERC20Debt | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | 2 | RECALL_CANDIDATE_ONLY |
| 1 | LiquidationLogic.executeCrossLiquidateERC721 | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | 2 | RECALL_CANDIDATE_ONLY |
| 2 | GenericLogic.calculateUserAccountDataForLiquidate | T1,T7,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | 3 | RECALL_CANDIDATE_ONLY |
| 3 | InterestLogic.updateInterestIndexs | T6 | top_n_overall;checkpoint_hit_evidence_marker | 1 | RECALL_CANDIDATE_ONLY |
| 4 | ValidateLogic.validateDepositERC721 | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | 1 | RECALL_CANDIDATE_ONLY |
| 5 | ValidateLogic.validateWithdrawERC721 | T2 | top_n_overall;checkpoint_hit_name_keyword | 1 | RECALL_CANDIDATE_ONLY |
| 6 | YieldStakingBase.batchStake | T5 | top_n_overall | 1 | RECALL_CANDIDATE_ONLY |
| 7 | LiquidationLogic._calculateDebtAmountFromERC721Collateral | T1,T7,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | 3 | RECALL_CANDIDATE_ONLY |
| 8 | LiquidationLogic.viewGetUserCrossLiquidateData | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | 2 | RECALL_CANDIDATE_ONLY |
| 9 | CrossLiquidation.crossLiquidateERC20 | T1,T5,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | 3 | RECALL_CANDIDATE_ONLY |
| 10 | YieldStakingBase.batchUnstake | T2,T5 | checkpoint_hit_name_keyword | 2 | RECALL_CANDIDATE_ONLY |
| 11 | YieldStakingBase.batchRepay | T5 | checkpoint_hit_name_keyword | 1 | RECALL_CANDIDATE_ONLY |
| 12 | GenericLogic.calculateUserAccountData | T7,T9 | t7t8_within_top;checkpoint_hit_evidence_marker | 2 | RECALL_CANDIDATE_ONLY |
| 13 | LiquidationLogic.executeCrossLiquidateERC20 | T1,T7 | t7t8_within_top;checkpoint_hit_name_keyword | 2 | RECALL_CANDIDATE_ONLY |
| 14 | IsolateLogic.executeIsolateLiquidate | T1,T7 | t7t8_within_top;checkpoint_hit_name_keyword | 2 | RECALL_CANDIDATE_ONLY |

Every row is RECALL_CANDIDATE_ONLY → NEEDS_RANKING/COMPLETION/REFUTATION before any finding.
