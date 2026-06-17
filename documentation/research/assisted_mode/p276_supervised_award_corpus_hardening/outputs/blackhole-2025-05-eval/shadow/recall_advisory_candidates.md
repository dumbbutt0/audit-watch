# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=25 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | Pair.burn | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | Pair.mint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | VotingEscrow.merge | T4 | top_n_overall | NEEDS_RANKING |
| 3.0 | VotingEscrow.split | T4 | top_n_overall | NEEDS_RANKING |
| 4.0 | VotingEscrow.withdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | Black.initialMint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | VoterV3.vote | T6 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 7.0 | RewardsDistributor.claim_many | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | VotingEscrow._createSplitNFT | T4 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | IRewarder.onReward | T3 | top_n_overall | NEEDS_RANKING |
| 11.0 | Pair._mint | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | Thenian.mintSecond | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 15.0 | Thenian.mintFirst | T8 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 16.0 | Black._mint | T8 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 17.0 | Black.mint | T8 | checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
