# Recall-First Harness — SHADOW advisory (wise)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=24 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | PendlePowerFarmToken.withdrawExactShares | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | WiseLending.withdrawExactShares | T2,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | PendlePowerFarmToken.depositExactAmount | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 3.0 | WiseLending.withdrawOnBehalfExactShares | T2,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | WiseLending.borrowExactAmount | T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | PositionNFTs.mintPositionForUser | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | PositionNFTs.approveMint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | PositionNFTs._mintPositionForUser | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | PendlePowerFarmToken.withdrawExactAmount | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | WiseLending.depositExactAmountMint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | WiseLending.solelyDepositMint | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | WiseCore._handleDeposit | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 12.0 | WiseCore._checkDeposit | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | WiseCore._checkMaxDepositValue | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | WiseCore._withdrawPureCollateralLiquidation | T2,T7 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
