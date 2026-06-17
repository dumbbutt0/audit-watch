# Recall-First Harness — SHADOW advisory (ronin)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=6 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 1.0 | V3Migrator.migrate | T1,T4,T9 | top_n_overall;top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | NonfungiblePositionManager.mint | T8 | top_n_overall;top_n_overall;t7t8_within_top;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | V3SwapRouter.katanaV3SwapCallback | T3 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | KatanaV3Pool.mint | T8 | top_n_overall;top_n_overall;t7t8_within_top;t7t8_within_top | NEEDS_RANKING |
| 8.0 | KatanaV3Pool.burn | T2 | top_n_overall;top_n_overall | NEEDS_RANKING |
| 10.0 | KatanaV3PoolBeacon.constructor | T4 | top_n_overall | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
