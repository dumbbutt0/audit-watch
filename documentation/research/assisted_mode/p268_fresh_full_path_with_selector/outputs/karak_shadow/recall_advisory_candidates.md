# Recall-First Harness — SHADOW advisory (karak)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=20 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | NativeVault.validateWithdrawalCredentials | T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | NativeVault.finishWithdrawal | T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | NativeVault._startSnapshot | T6 | top_n_overall | NEEDS_RANKING |
| 3.0 | NativeVault.startWithdrawal | T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | SlasherLib.requestSlashing | T5 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 5.0 | Vault.mint | T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 6.0 | Vault.startRedeem | T1,T2,T5 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 7.0 | NativeVault.validateSnapshotProofs | T5,T6 | top_n_overall | NEEDS_RANKING |
| 8.0 | NativeVault.withdrawableWei | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | Vault.finishRedeem | T1,T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | NativeVaultLib.validateWithdrawalCredentials | T2 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | SlasherLib.finalizeSlashing | T5 | checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | SlasherLib.cancelSlashing | T5 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | BeaconProofs.validateBalance | T6 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 16.0 | BeaconProofs.validateValidatorProof | T6 | checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
