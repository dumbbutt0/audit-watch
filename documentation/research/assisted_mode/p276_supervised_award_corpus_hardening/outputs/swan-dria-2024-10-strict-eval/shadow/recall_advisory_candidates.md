# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=13 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | BuyerAgent.withdraw | T2 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 1.0 | LLMOracleCoordinator.finalizeValidation | T5 | top_n_overall;checkpoint_hit_name_keyword | NEEDS_RANKING |
| 2.0 | BuyerAgent.purchase | T1,T3 | top_n_overall;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | LLMOracleCoordinator.withdrawPlatformFees | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 4.0 | Swan.purchase | T1,T3 | top_n_overall | NEEDS_RANKING |
| 5.0 | LLMOracleCoordinator._increaseAllowance | T1,T3 | top_n_overall | NEEDS_RANKING |
| 6.0 | LLMOracleCoordinator._authorizeUpgrade | T4 | top_n_overall | NEEDS_RANKING |
| 7.0 | LLMOracleRegistry._authorizeUpgrade | T4 | top_n_overall | NEEDS_RANKING |
| 8.0 | Swan._authorizeUpgrade | T4 | top_n_overall | NEEDS_RANKING |
| None | Statistics.sqrt | T9 | t9_math_name | NEEDS_RANKING |
| None | BuyerAgent._checkRoundPhase | T9 | t9_math_name | NEEDS_RANKING |
| None | BuyerAgent.getRoundPhase | T9 | t9_math_name | NEEDS_RANKING |
| None | BuyerAgent.setAmountPerRound | T9 | t9_math_name | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
