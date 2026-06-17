# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=14 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | PublicVault.redeemFutureEpoch | T1,T2,T3,T6 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | PublicVault._redeemFutureEpoch | T1,T2,T3,T6 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | PublicVault.redeem | T1,T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | PublicVault.withdraw | T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | PublicVault.processEpoch | T5,T6 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 5.0 | PublicVault.updateVaultAfterLiquidation | T2 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | PublicVault.transferWithdrawReserve | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | AstariaRouter.initialize | T2,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | WithdrawProxy.claim | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | LienToken.createLien | T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | PublicVault.mint | T3,T5,T8 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | AstariaRouter.mint | T8 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | AstariaRouter.newPublicVault | T5,T6,T8 | t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | LienToken.stopLiens | T5,T7 | t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
