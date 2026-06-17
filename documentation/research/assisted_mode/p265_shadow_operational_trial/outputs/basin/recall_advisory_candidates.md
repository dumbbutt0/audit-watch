# Recall-First Harness — SHADOW advisory (coverage_manifest)

**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** advisory_candidates=11 · guard_violations=0 · truncated=False

| p260_rank | locus | templates | inclusion | promotion_label |
|---|---|---|---|---|
| 0.0 | WellUpgradeable.upgradeTo | T4 | top_n_overall | NEEDS_RANKING |
| 1.0 | WellUpgradeable.upgradeToAndCall | T4 | top_n_overall | NEEDS_RANKING |
| 2.0 | WellUpgradeable._authorizeUpgrade | T4 | top_n_overall | NEEDS_RANKING |
| None | Stable2.calcLpTokenSupply | T9 | t9_math_name | NEEDS_RANKING |
| None | Stable2.calcReserve | T9 | t9_math_name | NEEDS_RANKING |
| None | Stable2.calcRate | T9 | t9_math_name | NEEDS_RANKING |
| None | Stable2.calcReserveAtRatioSwap | T9 | t9_math_name | NEEDS_RANKING |
| None | Stable2.calcReserveAtRatioLiquidity | T9 | t9_math_name | NEEDS_RANKING |
| None | Stable2.decodeWellData | T9 | t9_math_name | NEEDS_RANKING |
| None | Stable2._calcRate | T9 | t9_math_name | NEEDS_RANKING |
| None | Stable2.getScaledReserves | T9 | t9_math_name | NEEDS_RANKING |

Every candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion + refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.
