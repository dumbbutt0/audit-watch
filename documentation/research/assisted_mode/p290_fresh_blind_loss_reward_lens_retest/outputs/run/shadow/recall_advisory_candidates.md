# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=22 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | Liquidity._depositLiquidityAndIncreaseShare | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | StakingRewards.claimAllRewards | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | Pools.removeLiquidity | T2 | top_n_overall | NEEDS_RANKING |
| 3.0 | Pools.depositSwapWithdraw | T2,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 4.0 | Pools.depositDoubleSwapWithdraw | T2,T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 5.0 | Pools.withdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | DAO.withdrawPOL | T1,T2,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 7.0 | CollateralAndLiquidity.withdrawCollateralAndClaim | T2,T7 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 8.0 | Upkeep.step2 | T3 | top_n_overall | NEEDS_RANKING |
| 9.0 | Airdrop.allowClaiming | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 10.0 | CollateralAndLiquidity.liquidateUser | T1,T7 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 11.0 | CollateralAndLiquidity.maxWithdrawableCollateral | T2,T7 | t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 13.0 | DAO._finalizeApprovalBallot | T5 | checkpoint_hit_name_keyword | NEEDS_RANKING |
| 14.0 | Pools.deposit | T8 | t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 15.0 | USDS.mintTo | T8 | checkpoint_hit_name_keyword | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
