# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=14 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 1.0 | ConcreteMultiStrategyVault._withdraw | T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | ConcreteMultiStrategyVault.withdraw | T2,T3,T5 | top_n_overall;top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | ConcreteMultiStrategyVault.deposit | T3,T5,T8 | top_n_overall;top_n_overall;t7t8_within_top;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 7.0 | ConcreteMultiStrategyVault.mint | T3,T5,T8 | top_n_overall;top_n_overall;t7t8_within_top;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | ConcreteMultiStrategyVault._withdrawStrategyFunds | T2,T3,T9 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | ConcreteMultiStrategyVault.redeem | T1,T2,T3,T5 | top_n_overall;top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | ConcreteMultiStrategyVault.claimWithdrawal | T2 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | ProtectStrategy.executeBorrowClaim | T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 12.0 | ConcreteMultiStrategyVault.previewMint | T8 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | ConcreteMultiStrategyVault.maxMint | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | MultiStrategyVaultHelper.addOrReplaceStrategy | T6,T9 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 15.0 | ConcreteMultiStrategyVault.accruedProtocolFee | T6 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 16.0 | ConcreteMultiStrategyVault._convertToShares | T4,T8,T9 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 17.0 | ConcreteMultiStrategyVault._convertToAssets | T4,T8,T9 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
