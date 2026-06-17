# P208 — backtest scorecard (P204/P207 controls)

`python scripts/validate_p208_l3_readiness.py backtest` — all advisory, nothing submitted/routed.

| candidate | awarded | l3_status / tier | calibrated | high_promotion_allowed | expected | match |
|---|---|---|---|---|---|---|
| decent **H-01** setRouter→mint | high | PASS / L3_REAL_CONTRACT_POC | high | **true** | allow | ✅ |
| decent **M-03** receiveFromBridge | medium | FAIL / L3_REAL_CONTRACT_POC | medium | **false** | block | ✅ |
| vultisig **H-01** claim-fee-loss | high | PASS / L3_REAL_CONTRACT_POC | high | **true** | allow | ✅ |
| vultisig **M-03** cap-bypass | medium | FAIL / L3_REAL_CONTRACT_POC | medium | **false** | block | ✅ |

**4/4 controls classify exactly as expected.** The two genuine awarded Highs (each backed by an executed L3 PoC with
a control case, permissionless attacker, production unmodified, external-only mocks) are allowed; the two
over-rated/awarded-Medium controls (no material value movement) are blocked from High and calibrated to Medium.

Totals (incl. regressions, 10 candidates): expected_matches 10/10 · false_allows 0 · false_blocks 0 · allowed L3
Highs 2 · blocked ceiling-Highs 7 · schema pass 10/10. See `metrics.json`.
