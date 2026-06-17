# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=23 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | ERC20Gauges._burn | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | ERC20RebaseDistributor._mint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | SimplePSM.mint | T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 3.0 | SimplePSM.mintAndEnterRebase | T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | SurplusGuildMinter.unstake | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | SurplusGuildMinter.stake | T5 | top_n_overall | NEEDS_RANKING |
| 6.0 | ERC20RebaseDistributor._burn | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | ERC20RebaseDistributor.distribute | T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | LendingTerm.onBid | T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | ProfitManager.claimRewards | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | ERC20MultiVotes._burn | T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | LendingTerm.borrow | T5,T7 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | SurplusGuildMinter.updateMintRatio | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | LendingTerm._borrow | T7 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | RateLimitedMinter.mint | T5,T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
