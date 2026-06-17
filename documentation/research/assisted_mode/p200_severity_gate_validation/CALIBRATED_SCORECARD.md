# P200 — calibrated scorecard (post-freeze, predy-2024-05-holdout)

Awarded: **4 High (H-01..H-04) · 8 Medium (M-01..M-08)**. Blind ceiling `4aede343` · calibration `1e158f1e`,
both frozen before the seal opened.

## Per-surface: ceiling → calibrated → awarded reality
| id | surface | blind ceiling | calibrated label | mechanism-matched awarded | awarded sev | assessment |
|---|---|---|---|---|---|---|
| predy-01 | trade | HIGH | NEEDS_HARNESS | — | — | unawarded mechanism; correctly not High |
| predy-02 | reallocate | HIGH | **MEDIUM** | H-01/H-03/M-07 (diff mechanism) | High/Med | recall miss (griefing≠slot0) |
| predy-03 | execLiquidationCall | HIGH | NEEDS_HARNESS | — | — | unawarded; harness |
| predy-04 | supply/withdraw | HIGH | NEEDS_HARNESS | — | — | unawarded; harness |
| predy-05 | take | HIGH | NEEDS_HARNESS | — | — | unawarded; harness |
| predy-06 | LiquidationLogic.liquidate | HIGH | **MEDIUM** | **M-06** (exact) + **H-02** (secondary) | Med + High | ✓ M-06 demote correct; ✗ H-02 folded under Medium |
| predy-07 | isLiquidatable | HIGH | **HIGH_CONFIRMED** | M-04/M-08 (loose) | Medium | ✗ over-HIGH (oracle) |
| predy-08 | TradeLogic callback | HIGH | **HIGH_CONFIRMED** | — | — | unawarded High claim (recall FP) |
| predy-09 | PriceFeed.getSqrtPrice | HIGH | **HIGH_CONFIRMED** | **M-04** (exact) | Medium | ✗ over-HIGH (Chainlink staleness) |
| predy-10 | UniHelper TWAP | HIGH | **HIGH_CONFIRMED** | **M-03** (secondary) | Medium | ✗ over-HIGH (primary=TWAP unawarded; M-03=Medium) |
| predy-11 | SlippageLib.checkPrice | MEDIUM | MEDIUM | **M-01** (exact) | Medium | ✓ correct Medium |
| predy-12 | SettlementCallbackLib | HIGH | **HIGH_CONFIRMED** | — | — | unawarded High claim (recall FP) |
| predy-13 | GammaTradeMarket._executeTrade | HIGH | NEEDS_HARNESS | — | — | unawarded; harness |
| predy-14 | PerpMarketV1.executeOrderV3 | HIGH | NEEDS_HARNESS | — | — | unawarded; harness |
| predy-15 | DecayLib | MEDIUM | MEDIUM | — | — | correctly Medium |
| predy-16 | Perp.reallocate | HIGH | **HIGH_CONFIRMED** | H-01/H-03 (diff mechanism) | High | ✗ unawarded mechanism High claim (recall miss on the awarded one) |

## Distribution
| | ≥High | Medium | Harness | 
|---|---|---|---|
| blind ceiling | **14/16** | 2 | 0 |
| calibrated | **6/16** | 4 | 6 |

The gate moved 8 surfaces off the HIGH ceiling (2→Medium, 6→Harness).

## The severity-scoring subset (mechanism-matched awarded findings, n=5 Medium + 1 High)
| matched | awarded sev | ceiling | calibrated | outcome |
|---|---|---|---|---|
| predy-06 → M-06 | Medium | High | Medium | ✓ **fixed over-HIGH** |
| predy-07 → M-04 (loose) | Medium | High | High | ✗ over-HIGH retained |
| predy-09 → M-04 | Medium | High | High | ✗ over-HIGH retained |
| predy-10 → M-03 | Medium | High | High | ✗ over-HIGH retained |
| predy-11 → M-01 | Medium | Medium | Medium | ✓ (never over-rated) |
| predy-06 → H-02 (secondary) | High | High | Medium(surface) | ✗ genuine-High folded under Medium |

- **Over-HIGH on matched awarded-Medium: ceiling 4/5 → calibrated 3/5** (gate fixed **1**: predy-06). ~25% reduction.
- **Still over-HIGH: 3/5, all oracle/precision** (predy-07/09 Chainlink staleness = M-04; predy-10 negative-tick = M-03).
- **Genuine-High found by mechanism: 1 (H-02)** — graded Medium at surface level (multi-mechanism folding).
- **No clean false-demotion** of a separately-found awarded High to Medium/None.
- **Unawarded HIGH_CONFIRMED: 3** (predy-08/12/16) — recall false-positives, not severity-gate failures.
