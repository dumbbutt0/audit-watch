# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=23 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | RTokenP1.redeemCustom | T1,T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | RTokenP1.redeemTo | T1,T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | StRSRP1.unstake | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 3.0 | StRSRP1.cancelUnstake | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | DistributorP1.distribute | T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | BackingManagerP1.rebalance | T1 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | RTokenP1.issueTo | T5 | top_n_overall | NEEDS_RANKING |
| 7.0 | StRSRP1Votes._mint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | StRSRP1.withdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | StRSRP1._burn | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | RTokenP1.redeem | T1,T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | into.bidWithCallback | T3 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | BackingManagerP1.settleTrade | T1,T2,T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | StRSRP1.seizeRSR | T7 | t7t8_within_top | NEEDS_RANKING |
| 15.0 | StRSRP1Votes._burn | T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
