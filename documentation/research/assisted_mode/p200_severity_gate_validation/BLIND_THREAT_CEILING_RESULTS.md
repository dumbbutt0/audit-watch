# P200 — blind threat-ceiling results (FREEZE 1)

16 Sonnet subagents, one per pre-registered surface, each on production `deep_trace.md` (`ef93a6c2`) + verbatim
source only. Blind firewall: prompts token-scanned pre-run (CLEAN); raw outputs preserved verbatim in
`raw_outputs/predy-*.json`; **outputs token-scanned for answer-key leakage = CLEAN** (no finding-ID/issue-link
cited by any agent — confirms blindness); all 16 valid JSON. **FREEZE 1 hash** (md5 first-8 of concatenated raw
outputs): `4aede343`.

## Verdict distribution (the threat ceiling, pre-calibration)
| verdict | count |
|---|---|
| CRITICAL_THREAD | 0 |
| **HIGH_THREAD** | **14** |
| **MEDIUM_THREAD** | **2** (predy-11 slippage, predy-15 dutch-auction decay) |
| DEAD_END / NEEDS_MORE_CONTEXT | 0 |

**14/16 ≥ HIGH (87.5%).** This reproduces the P199 over-HIGH skew out-of-sample: the deep-trace verdict is a
worst-case *threat ceiling*, and almost every examined surface ceils at HIGH. The two MEDIUM verdicts land exactly
on the Medium-leaning surfaces (precision/slippage, dutch-auction truncation) — the stack *can* grade Medium when
the impact is intrinsically bounded, but defaults to HIGH otherwise.

## Per-surface summary (blind)
| id | surface | primary mechanism (blind) | verdict | selected | NEEDS_HARNESS |
|---|---|---|---|---|---|
| predy-01 | PredyPool.trade | unauthorized vault takeover / settlement-callback take() | HIGH | 2 | 2 |
| predy-02 | PredyPool.reallocate | permissionless reallocate + unvalidated settlementData | HIGH | 2 | 2 |
| predy-03 | PredyPool.execLiquidationCall | unbounded closeRatio / settlement injection / recipient=0 | HIGH | 3 | 3 |
| predy-04 | PredyPool.supply/withdraw | stale-rate share mint / first-depositor inflation | HIGH | 2 | 2 |
| predy-05 | PredyPool.take | locker take() amount uncapped / reentrancy | HIGH | 2 | 3 |
| predy-06 | LiquidationLogic.liquidate | recipient-revert DoS / partial-close bad-debt dodge | HIGH | 2 | 2 |
| predy-07 | PositionCalculator.isLiquidatable | oracle no-staleness / caller-supplied feeAmount | HIGH | 2 | 2 |
| predy-08 | TradeLogic.callTradeAfterCallback | unchecked msg.sender-as-hook / checkSafe-after-callback | HIGH | 2 | 2 |
| predy-09 | PriceFeed.getSqrtPrice | Chainlink no staleness/round-completeness; Pyth overflow | HIGH | 2 | 3 |
| predy-10 | UniHelper.getSqrtTWAP | TWAP window degrades to spot at low cardinality | HIGH | 2 | 1 |
| predy-11 | SlippageLib.checkPrice | short/long bound-label inversion (sandwich) | **MEDIUM** | 1 | 2 |
| predy-12 | SettlementCallbackLib | buy() returns maxQuote-quoteAmount not -quoteAmountToUni (pool short) | HIGH | 2 | 2 |
| predy-13 | GammaTradeMarket._executeTrade | filler check AFTER trade; minMargin==0 bypass | HIGH | 1 | 2 |
| predy-14 | PerpMarketV1.executeOrderV3 | filler check after callback; verify-after-execute | HIGH | 2 | 2 |
| predy-15 | DecayLib.decay/decay2 | division truncation bias / overflow DoS | **MEDIUM** | 2 | 1 |
| predy-16 | Perp.settleUserBalance | stale-index rebalance settle / pool-can-go-negative | HIGH | 3 | 2 |

Recall observation (not the phase's metric): the blind stack re-derives many plausible predy mechanisms
(oracle-staleness, TWAP-to-spot, filler-ordering, settlement accounting, share inflation) — consistent with P198
(recall generalizes). The **severity** of those verdicts is what P200 tests. Whether each maps to an *awarded*
finding is determined only post-freeze (Step 6); these are blind candidates, **not** confirmed awarded bugs.
