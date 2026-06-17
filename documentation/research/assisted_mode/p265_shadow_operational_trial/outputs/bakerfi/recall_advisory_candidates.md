# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=17 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | Vault.deposit | T3,T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | Vault.rebalance | T1,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | Vault.withdraw | T2,T5 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | StrategyLeverage._repayAndWithdraw | T2,T3 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | StrategyLeverage.harvest | T1 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | Vault.convertToShares | T4,T8,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | Vault.convertToAssets | T4,T8,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 7.0 | BKR._mint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | StrategyLeverage._undeploy | T3 | top_n_overall | NEEDS_RANKING |
| 9.0 | StrategyAAVEv3.initialize | T7 | top_n_overall;t7t8_within_top | NEEDS_RANKING |
| 10.0 | BKR._burn | T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 12.0 | Settings.setMaxDepositInETH | T8 | t7t8_within_top | NEEDS_RANKING |
| 14.0 | StrategyLeverage._initializeStrategyBase | T7,T9 | t7t8_within_top | NEEDS_RANKING |
| None | UseLeverage.calculateLeverageRatio | T9 | t9_math_name | NEEDS_RANKING |
| None | UseLeverage.calcDeltaPosition | T2,T7,T9 | t9_math_name | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
