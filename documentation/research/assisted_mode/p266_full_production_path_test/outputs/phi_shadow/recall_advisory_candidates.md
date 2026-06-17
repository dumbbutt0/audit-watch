# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=18 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | PhiFactory.signatureClaim | T2,T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | PhiFactory.merkleClaim | T2,T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | CuratorRewardsDistributor.distribute | T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 3.0 | PhiFactory._validateAndUpdateClaimState | T2,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | PhiNFT1155.claimFromFactory | T2,T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | Cred._handleTrade | T5 | top_n_overall | NEEDS_RANKING |
| 6.0 | Cred._executeBatchTrade | T5 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 7.0 | Cred._updateCuratorShareBalance | T1 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | PhiNFT1155.mint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | PhiFactory._processClaim | T2,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | RewardControl.depositBatch | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | RewardControl.withdrawWithSig | T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 12.0 | RewardControl.deposit | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | CuratorRewardsDistributor.deposit | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | PhiRewards.depositRewards | T8,T9 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
