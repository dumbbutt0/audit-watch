# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=15 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | Pool._redeem | T1,T2,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | Pool._create | T8 | top_n_overall;t7t8_within_top | NEEDS_RANKING |
| 2.0 | PreDeposit.claim | T2,T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | Pool.redeem | T1,T2,T5,T8 | top_n_overall;top_n_overall;t7t8_within_top;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | Pool.create | T5,T8 | top_n_overall;top_n_overall;t7t8_within_top;t7t8_within_top | NEEDS_RANKING |
| 8.0 | PreDeposit.deposit | T5,T8 | top_n_overall;top_n_overall;t7t8_within_top;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | PreDeposit._deposit | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | Pool.simulateRedeem | T1,T2,T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | BalancerRouter.joinBalancerAndPredeposit | T8 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | Pool.simulateCreate | T8 | t7t8_within_top | NEEDS_RANKING |
| 15.0 | Auction.endAuction | T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 16.0 | Auction.claimBid | T2,T5,T6 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 17.0 | Distributor.claim | T2,T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 18.0 | Pool.initialize | T5,T6 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 19.0 | Pool.claimFees | T2 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
