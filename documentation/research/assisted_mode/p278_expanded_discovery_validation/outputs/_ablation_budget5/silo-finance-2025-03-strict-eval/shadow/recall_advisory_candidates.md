# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=17 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | SiloVault.withdraw | T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | SiloVault.redeem | T1,T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | SiloVault.updateWithdrawQueue | T2,T5,T6 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | SiloVault._accruedFeeShares | T6 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | SiloVault.maxMint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | SiloVault.claimRewards | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | PublicAllocator.reallocateTo | T2 | top_n_overall | NEEDS_RANKING |
| 7.0 | SiloVault.deposit | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | SiloVault.mint | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | SiloVault.maxRedeem | T1,T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | SiloVault._maxWithdraw | T2 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | SiloVault._convertToShares | T4,T8,T9 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | SiloVault._convertToAssets | T4,T8,T9 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | SiloVault._accrueFee | T6 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | SiloVault._maxDeposit | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
