# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=19 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | AccountingManager.executeWithdraw | T2,T5,T9 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | AccountingManager.retrieveTokensForWithdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | AccountingManager.executeDeposit | T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 3.0 | AccountingManager.calculateWithdrawShares | T2,T5,T9 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | CompoundConnector.withdrawOrBorrow | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | AccountingManager.calculateDepositShares | T5,T8,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | UNIv3Connector.openPosition | T8 | top_n_overall;t7t8_within_top | NEEDS_RANKING |
| 7.0 | PositionRegistry.addVault | T4 | top_n_overall | NEEDS_RANKING |
| 8.0 | PendleConnector.depositIntoMarket | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | SNXV3Connector.claimRewards | T2,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | CurveConnector.openCurvePosition | T6,T8 | t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | CurveConnector.harvestPrismaRewards | T1 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | DolomiteConnector.withdraw | T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | AccountingManager.startCurrentWithdrawGroup | T2,T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | AccountingManager.fulfillCurrentWithdrawGroup | T2,T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
