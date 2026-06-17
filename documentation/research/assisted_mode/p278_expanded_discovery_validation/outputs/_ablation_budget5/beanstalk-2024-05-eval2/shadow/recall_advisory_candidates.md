# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=16 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | IBeanstalk.cancelPodListing | T6 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | ReseedSilo.init | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | EnrootFacet.enrootDeposits | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 3.0 | ReseedSilo.reseedSiloDeposit | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | Invariable.getTokenEntitlementsAndBalances | T1,T3 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 5.0 | L2ContractMigrationFacet.redeemDepositsAndInternalBalances | T1,T2,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | TokenSilo._transferDeposits | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | ReseedBean.mintAndSync | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | L2ContractMigrationFacet.addMigratedDepositsToAccount | T1,T4,T8,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | LibConvert._withdrawTokens | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | ReseedBarn.mintFertilizers | T1,T3,T8 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | ReseedField.init | T1,T4,T9 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | LibTokenSilo.removeDepositFromAccount | T8,T9 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | ReseedBean.mintUnripeToExternal | T1,T3,T8 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | FieldFacet._harvest | T1 | checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
