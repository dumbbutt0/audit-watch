# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=15 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | V3Vault.liquidate | T1,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | V3Vault._withdraw | T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | V3Vault.withdraw | T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | V3Vault.redeem | T1,T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | V3Vault.withdrawReserves | T2,T3 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | Automator.withdrawBalances | T1,T2,T3 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | V3Vault.deposit | T3,T8 | top_n_overall;top_n_overall;t7t8_within_top;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | V3Vault.mint | T3,T8 | top_n_overall;top_n_overall;t7t8_within_top;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | V3Utils.swapAndMint | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | V3Vault.transform | T1,T3 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | V3Vault._deposit | T3,T8 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | Swapper._routerSwap | T1,T3 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | AutoCompound.withdrawBalances | T1,T2,T3 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 15.0 | V3Utils._swapAndPrepareAmounts | T8 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 16.0 | Automator._transferToken | T1,T3 | checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
