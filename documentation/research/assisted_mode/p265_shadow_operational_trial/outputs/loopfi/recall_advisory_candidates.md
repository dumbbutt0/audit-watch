# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=13 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | MultiFeeDistribution.claimFromConverter | T2,T4,T5,T9 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | MultiFeeDistribution._withdrawTokens | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | MultiFeeDistribution._withdrawExpiredLocksFor | T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 3.0 | MultiFeeDistribution._stake | T5,T6 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | MultiFeeDistribution.vestTokens | T5 | top_n_overall | NEEDS_RANKING |
| 5.0 | MultiFeeDistribution.withdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | MultiFeeDistribution.claimBounty | T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | PoolV3.deposit | T3,T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | PoolV3.mint | T3,T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | PoolV3.withdraw | T2,T3,T5 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | PoolV3.redeem | T1,T2,T3,T5 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | MultiFeeDistribution.stake | T6 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | CDPVault.liquidatePosition | T1,T5,T7 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
