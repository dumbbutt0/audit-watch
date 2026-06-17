# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=11 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | StarklaneEscrow._withdrawFromEscrow | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 1.0 | Starklane.withdrawTokens | T2 | top_n_overall;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 2.0 | StarklaneEscrow._depositIntoEscrow | T8 | top_n_overall;t7t8_within_top;checkpoint_hit_name_keyword;checkpoint_hit_evidence_marker | NEEDS_RANKING |
| 3.0 | Starklane.depositTokens | T2,T8 | top_n_overall;t7t8_within_top | NEEDS_RANKING |
| 4.0 | StarklaneMessaging.addMessageHashForAutoWithdraw | T2 | top_n_overall | NEEDS_RANKING |
| 5.0 | that._consumeMessageAutoWithdraw | T2 | top_n_overall | NEEDS_RANKING |
| 6.0 | UUPSOwnableProxied._authorizeUpgrade | T4 | top_n_overall | NEEDS_RANKING |
| None | Cairo.uint256ArraySerialize | T9 | t9_math_name | NEEDS_RANKING |
| None | Cairo.uint256ArrayDeserialize | T9 | t9_math_name | NEEDS_RANKING |
| None | Cairo.cairoStringArraySerialize | T9 | t9_math_name | NEEDS_RANKING |
| None | Cairo.cairoStringArrayDeserialize | T9 | t9_math_name | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
