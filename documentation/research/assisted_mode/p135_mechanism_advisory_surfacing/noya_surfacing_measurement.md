# P135 — Noya Surfacing Measurement

## Volumes
| Mode | total | by detector | by status | deep-pass recs | standalone queue |
|---|---|---|---|---|---|
| production default | 26 | CPA 7, AC 9, units 10 | advisory 16, report_only 10 | 10 | 0 |
| eval (`--eval`) | 39 | CPA 7, AC 9, units 10, STC 10, RPL 3 | advisory 16, report_only 10, research_only 13 | 10 | 39 |
| master gate off | 0 | — | — | 0 | 0 |

units_invariant produced 45 raw hits → capped to its **10 high-risk** entries (confidence-prioritized cap, so
the H-01 Chainlink decimals MISS is kept); STC 11 → 10 (cap).

## P133 target routing (do the missed/partial cases now reach review?)
| Awarded | P133 | Reaches review at PRODUCTION default via |
|---|---|---|
| H-01 ChainlinkOracleConnector.getValue | **MISS** | units_invariant ✅ |
| H-13 BalancerConnector._getPositionTVL | **MISS** | connector_position_accounting ✅ |
| H-14 BalancerConnector.totalLpBalanceOf | **MISS** | units_invariant + arithmetic_conservation ✅ |
| H-06 AerodromeConnector._getPositionTVL | PARTIAL | connector_position_accounting + arithmetic_conservation ✅ |
| H-22 PendleConnector._getPositionTVL | PARTIAL | units_invariant + arithmetic_conservation ✅ |
| H-15 SiloConnector._getPositionTVL | PARTIAL | arithmetic_conservation ✅ |
| H-19 MorphoBlueConnector._getPositionTVL | HIT | connector_position_accounting ✅ |

- **All 3 P133 MISS reach review at production default.** All 7 awarded targets (excl. H-03) reach review at
  production default; research-only detectors (STC/RPL) add corroborating advisories in eval mode.
- **H-03** `NoyaValueOracle._getValue` → receives a **deep_pass_value_provenance recommendation** (review_context),
  not a detector finding — closing the one true residual via the existing prompt.
- **Bonus** (eval, research-only RPL): H-23 `transferBetweenAccounts` + H-18 `closeBorrowPosition` +
  SNXV3.createAccount surfaced as research-only advisory context.

## Suppression / caps
- research-only (STC/RPL, 13 entries) suppressed at production default; surfaced only in eval (`--eval`).
- caps suppressed 35 units raw hits (45→10) + 1 STC (11→10), keeping the highest-confidence/high-risk entries.

## Attachment
- 0 attached (noya has no `merged_findings.json` — never ran the full pipeline → all advisories are standalone).
  Attachment is exercised by the unit test on a synthetic candidate.
