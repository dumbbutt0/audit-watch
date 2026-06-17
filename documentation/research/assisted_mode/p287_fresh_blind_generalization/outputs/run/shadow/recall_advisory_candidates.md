# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=13 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | NodeDelegator.transferBackToLRTDepositPool | T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | LRTDepositPool.depositAsset | T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | LRTDepositPool.addNodeDelegatorContractToQueue | T5 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | LRTDepositPool._mintRsETH | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | RSETH.mint | T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | LRTDepositPool.getTotalAssetDeposits | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | LRTDepositPool.getRsETHAmountToMint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | RSETH.burnFrom | T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | LRTDepositPool.getAssetDistributionData | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | LRTDepositPool.transferAssetToNodeDelegator | T6 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | NodeDelegator.depositAssetIntoStrategy | T5,T8,T9 | t7t8_within_top | NEEDS_RANKING |
| 11.0 | LRTConfig.addNewSupportedAsset | T8 | t7t8_within_top | NEEDS_RANKING |
| 12.0 | LRTConfig.updateAssetDepositLimit | T8 | t7t8_within_top | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
