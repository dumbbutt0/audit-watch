# P287 — REVEAL_AND_SCORE (kelp-2023-11, opened AFTER pre-reveal freeze)

Answer key opened only after `outputs/pre_reveal_freeze.json`. Awarded H/M = 5 (3H/2M). Full data:
`outputs/reveal_score.json`.

## Awarded findings through the funnel
| id | area | surfaced | routed | queued | READY | PoC | match level |
|---|---|---|---|---|---|---|---|
| **H-01** | Chainlink price discrepancy/staleness (LRTOracle / getRsETHAmountToMint) | ✓ | ✓ | ✓ | ✓ | **PASS_SUPPORTED** | **STRONG_MECHANISM_MATCH** |
| H-02 | mints less rsETH — deposit-before-calc (depositAsset/getRsETHAmountToMint) | ✓ | ✓ | ✓ | ✓ | — | SAME_AREA_WRONG_MECHANISM |
| H-03 | first-staker rsETH price manipulation (getRSETHPrice donation) | ✗ | — | — | — | — | SUBSYSTEM_ONLY_RECALL |
| M-01 | strategy update → wrong issuance (getTotalAssetDeposits) | ✓ | ✓ | ✓ | ✗ | — | SUBSYSTEM_ONLY_RECALL |
| M-02 | slippage control on depositAsset | ✓ | ✓ | ✗ | ✗ | — | SUBSYSTEM_ONLY_RECALL |

## Pre-reveal candidate classification
- **LRTDepositPool.getRsETHAmountToMint → STRONG_MECHANISM_MATCH (H-01)**, PoC PASS_SUPPORTED. The pre-reveal mechanism
  (mint valuation consumes Chainlink `latestAnswer()` with no staleness/normalization guard) is the same root cause +
  locus as H-01 (the protocol trusts a stale-capable Chainlink price in the rsETH valuation). Also SAME_AREA to H-02
  (same function, different mechanism). NOT a false positive; NOT over-claimed to EXACT (the awarded H-01 frames the
  exploit as heartbeat-deviation arbitrage; the PoC proved the staleness-consumption primitive that underlies it).

## Honest scoring notes
- **1 STRONG awarded recovery, pre-reveal, PoC-supported** (H-01). 0 EXACT (conservative; see above).
- **4/5 awarded loci surfaced**; the one fully missed locus is `getRSETHPrice` (H-03 donation/inflation) — a recall gap.
- H-02/M-01/M-02 are SAME_AREA/SUBSYSTEM: the pipeline surfaced+queued the right functions but did not derive their
  specific mechanisms (asset-transfer ordering / strategy-update accounting / slippage) — those are not oracle/value-flow
  deviations the current evidence layer derives.
- **severe concluded/reportable FP = 0**; 0 false positives; 0 fabricated passes. No status beyond advisory set.
