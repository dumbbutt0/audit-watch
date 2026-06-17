# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=11 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | CollateralTracker.settleMint | T1,T2,T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | CollateralTracker.settleLiquidation | T1,T2,T5,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | CollateralTracker.deposit | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | CollateralTracker.mint | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 5.0 | CollateralTracker.withdraw | T2,T3,T7 | top_n_overall;top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | CollateralTracker.redeem | T1,T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 7.0 | CollateralTracker._accrueInterest | T6,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | CollateralTracker.settleBurn | T1,T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | PanopticPool._mintOptions | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | CollateralTracker._updateBalancesAndSettle | T1,T2,T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | PanopticPool._burnOptions | T1,T2,T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
