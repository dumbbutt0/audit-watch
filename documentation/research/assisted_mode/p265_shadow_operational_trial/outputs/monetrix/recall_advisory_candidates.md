# Recall-First Harness — SHADOW advisory (monetrix)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=19 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | sUSDM.cooldownShares | T2,T5 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | sUSDM.cooldownAssets | T2,T5 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | IMonetrixConfigReader.tradeableAssets | T6 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | IMonetrixConfigReader.spotToPerp | T6 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | IMonetrixConfigReader.isSpotWhitelisted | T6 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 5.0 | InsuranceFund.withdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | MonetrixVault.distributeYield | T5,T6 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | MonetrixVault.claimRedeem | T1,T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 8.0 | MonetrixVault.deposit | T5,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 9.0 | MonetrixVault.settle | T1,T2,T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | MonetrixVault.fundRedemptions | T5 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 11.0 | MonetrixVault.emergencyBridgePrincipalFromL1 | T4 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 12.0 | sUSDM.claimUnstake | T2,T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 13.0 | MonetrixVault.bridgePrincipalFromL1 | T5 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | MonetrixVault.bridgeYieldFromL1 | T5 | checkpoint_hit_evidence_marker | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
