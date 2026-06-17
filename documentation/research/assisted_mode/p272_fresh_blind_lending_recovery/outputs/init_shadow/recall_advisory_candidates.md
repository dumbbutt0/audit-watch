# Recall-First Harness — SHADOW advisory (init)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=20 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | PosManager.removeCollateralWLpTo | T3,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | LendingPool.mint | T3,T6,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | LendingPool.accrueInterest | T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 3.0 | WLpMoeMasterChef.harvest | T1 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | InitCore.mintTo | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 5.0 | MarginTradingHook.repayDebt | T7,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | LendingPool.burn | T2,T3,T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | PosManager._harvest | T1 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | MarginTradingHook.addCollateral | T7,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | InitCore._liquidateInternal | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | InitCore.burnTo | T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | LendingPool.borrow | T3,T6 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | PosManager.harvestTo | T1 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | MoneyMarketHook._handleDeposit | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | Config.getModeConfig | T7 | t7t8_within_top | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
