# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=18 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | LibStaking.depositWithConfirm | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | SubnetActorManagerFacet.leave | T5 | top_n_overall | NEEDS_RANKING |
| 2.0 | SubnetActorManagerFacet.addBootstrapNode | T5 | top_n_overall | NEEDS_RANKING |
| 3.0 | LibActivity.processConsensusClaim | T2,T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | LibGateway.storeBottomUpCheckpoint | T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | LibStakingReleaseQueue.claim | T2,T5 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | LibValidatorSet.confirmWithdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | SubnetActorActivityFacet.batchSubnetClaim | T2,T5,T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | LibStakingReleaseQueue.setLockDuration | T5 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | SubnetActorCheckpointingFacet.submitCheckpoint | T5,T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | GatewayManagerFacet.register | T7 | t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | CheckpointingFacet.commitCheckpoint | T6 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 12.0 | GatewayGetterFacet.getIncompleteCheckpoints | T6 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | SubnetActorCheckpointingFacet.ensureValidCheckpoint | T6 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 17.0 | GatewayGetterFacet.getIncompleteCheckpointHeights | T6 | checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
