# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=18 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | BorrowerOperations._adjustTrove | T2,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | TroveManager._liquidateRecoveryMode | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | CollateralConfig.initialize | T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | StabilityPool.offset | T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | TroveManager.liquidate | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 5.0 | BorrowerOperations.openTrove | T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | TroveManager._liquidateNormalMode | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 7.0 | TroveManager._removeTroveOwner | T7,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | ActivePool.manualRebalance | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | that.setAddresses | T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | TroveManager.redeemCloseTrove | T1,T2,T7 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | TroveManager.closeTrove | T7 | t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | ActivePool.pullCollateralFromBorrowerOperationsOrDefaultPool | T7 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | LUSDToken.mint | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | TroveManager._closeTrove | T7 | t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
