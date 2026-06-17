# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=16 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | AbstractYieldStrategy._mintSharesGivenAssets | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | AbstractYieldStrategy._burnShares | T1,T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | AbstractYieldStrategy._withdraw | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | AbstractSingleSidedLP._redeemShares | T1,T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | AbstractRewardManager.updateRewardToken | T4,T6,T9 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 5.0 | AbstractRewardManager.migrateRewardPool | T1,T4,T9 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | AbstractRewardManager._claimVaultRewards | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 7.0 | AbstractYieldStrategy.redeemNative | T1,T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | AbstractRewardManager.claimRewardTokens | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | AbstractWithdrawRequestManager.finalizeAndRedeemWithdrawRequest | T1,T2,T5 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | BaseLPLib.finalizeAndRedeemWithdrawRequest | T1,T2,T5 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | AbstractYieldStrategy.mintShares | T3,T8 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | AbstractYieldStrategy.burnShares | T1,T2 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | AbstractYieldStrategy._accrueFees | T6 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | AbstractRewardManager._claimRewardToken | T2 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
