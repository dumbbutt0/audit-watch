# Recall-First Harness — SHADOW advisory (gondi)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=15 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | MultiSourceLoan._processOffersFromExecutionData | T3,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | Pool.withdraw | T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | Pool.redeem | T1,T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | Pool.mint | T3,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | WithdrawalQueue.mint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 5.0 | WithdrawalQueue.withdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | MultiSourceLoan.mergeTranches | T4,T8 | top_n_overall;t7t8_within_top | NEEDS_RANKING |
| 7.0 | MultiSourceLoan._mergeTranches | T4,T8 | top_n_overall;t7t8_within_top | NEEDS_RANKING |
| 8.0 | Pool.constructor | T2,T5 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | Pool.deployWithdrawalQueue | T2,T5 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | Pool._queueClaimAll | T2,T5,T6 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | LiquidationDistributor.distribute | T6 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 12.0 | UserVault.burnAndWithdraw | T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | Pool._withdraw | T2,T3 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | AuctionWithBuyoutLoanLiquidator.settleWithBuyout | T1,T2,T4,T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
