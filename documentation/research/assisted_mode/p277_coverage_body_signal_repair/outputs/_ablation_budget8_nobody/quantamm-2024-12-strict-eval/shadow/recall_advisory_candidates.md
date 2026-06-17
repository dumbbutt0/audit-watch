# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=21 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | UpliftOnlyExample.onAfterRemoveLiquidity | T3 | top_n_overall | NEEDS_RANKING |
| 1.0 | LPNFT.burn | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | AntiMomentumUpdateRule._getWeights | T4,T9 | top_n_overall | NEEDS_RANKING |
| 3.0 | MomentumUpdateRule._getWeights | T4,T9 | top_n_overall | NEEDS_RANKING |
| 4.0 | PowerChannelUpdateRule._getWeights | T4,T9 | top_n_overall | NEEDS_RANKING |
| 5.0 | LPNFT.mint | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 6.0 | UpliftOnlyExample.constructor | T2 | top_n_overall | NEEDS_RANKING |
| 7.0 | ChannelFollowingUpdateRule._getWeights | T4,T9 | top_n_overall | NEEDS_RANKING |
| 8.0 | DifferenceMomentumUpdateRule._getWeights | T4,T9 | top_n_overall | NEEDS_RANKING |
| 9.0 | MinimumVarianceUpdateRule._getWeights | T4,T9 | top_n_overall | NEEDS_RANKING |
| 10.0 | QuantAMMWeightedPool._calculateCurrentBlockWeight | T6,T9 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| None | VectorRuleQuantAMMStorage._quantAMMUnpack128Matrix | T9 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| None | QuantAMMMathMovingAverage._calculateQuantAMMMovingAverage | T9 | checkpoint_hit_evidence_marker | NEEDS_RANKING |
| None | UpliftOnlyExample.getPoolLPTokenValue | T9 | t9_math_name | NEEDS_RANKING |
| None | ScalarQuantAMMBaseStorage.quantAMMUnpack32Array | T9 | t9_math_name | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
