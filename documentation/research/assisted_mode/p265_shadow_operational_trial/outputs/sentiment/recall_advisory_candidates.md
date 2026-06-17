# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=16 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | Pool.withdraw | T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | PositionManager.liquidate | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | SuperPool._deposit | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | SuperPool.maxWithdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | SuperPool.maxRedeem | T1,T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | Pool.rebalanceBadDebt | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | SuperPool._withdraw | T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 7.0 | Pool.deposit | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | SuperPool.deposit | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | SuperPool.mint | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | PositionManager.liquidateBadDebt | T1,T7 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | SuperPool._maxWithdraw | T2 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | SuperPool.withdraw | T2,T3 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | SuperPool.redeem | T1,T2,T3 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 15.0 | Pool.accrue | T6 | checkpoint_hit_name_keyword;checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
