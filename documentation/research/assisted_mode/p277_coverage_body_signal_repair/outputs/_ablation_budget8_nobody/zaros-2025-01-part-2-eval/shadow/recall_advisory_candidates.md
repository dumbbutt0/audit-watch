# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=17 · guard_violations=0 · truncated=True

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | VaultRouterBranch.deposit | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | CreditDelegationBranch.withdrawUsdTokenFromMarket | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | PerpsEngineConfiguration.removeCollateralFromLiquidationPriority | T7 | top_n_overall;t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | FeeDistributionBranch.convertAccumulatedFeesToWeth | T4,T9 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | Market.getCreditDepositsValueUsd | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | Market.rehydrateCreditDepositsValueCache | T8,T9 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | RootUpgrade.upgrade | T4 | top_n_overall | NEEDS_RANKING |
| 7.0 | CreditDelegationBranch.settleVaultsDebt | T1,T2,T5 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | VaultRouterBranch.getIndexTokenSwapRate | T1,T2,T6,T9 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 9.0 | VaultRouterBranch.redeem | T1,T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 10.0 | MarketMakingEngineConfiguration.distributeProtocolAssetReward | T6 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | LiquidationBranch.liquidateAccounts | T1,T7 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 12.0 | VaultRouterBranch.getVaultAssetSwapRate | T8,T9 | t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | PerpsEngineConfigurationBranch.configureCollateralLiquidationPriority | T7 | t7t8_within_top;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 14.0 | UsdToken.mint | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
