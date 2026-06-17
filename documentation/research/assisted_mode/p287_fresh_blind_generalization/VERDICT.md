# P287 — VERDICT

## Verdict: **A — FULL_PATH_GENERALIZED_WITH_AWARDED_RECOVERY**
## Bottleneck: **I — FULL_PATH_GENERALIZED**

## Core question
Can the FROZEN post-P286 stack produce ≥1 high-quality READY/PoC-supported candidate on a fresh target with confirmed
awarded H/M, before seeing the findings? **Answer: yes.** On kelp-2023-11 (never scored by the pipeline), the stack
carried `LRTDepositPool.getRsETHAmountToMint` surface → route → P284 D4.6 oracle-normalization evidence → READY →
Tier-C PoC (3/3 PASS), pre-reveal; post-reveal it is a **STRONG_MECHANISM_MATCH to awarded H-01** (Chainlink staleness
in the rsETH mint valuation). severe FP=0.

## Scorecard vs the A-bar
| criterion | result |
|---|---|
| ≥1 exact/strong awarded H/M mechanism recovered pre-reveal | ✔ (H-01 STRONG) |
| READY and/or PoC support | ✔ (READY + PoC PASS_SUPPORTED) |
| severe concluded/reportable FP = 0 | ✔ |
| no production-authority leakage | ✔ (advisory; frozen/forbidden byte-identical) |
| frozen stack unchanged | ✔ (re-hashed) |
| active audit unchanged | ✔ |

## What generalized
- **The P284 invariant-delta D4.6 oracle-normalization lens** — built/validated on the eval corpus — fired correctly on
  fresh, unseen code (the rsETH mint valuation consuming raw `latestAnswer()` with no staleness guard).
- **The P285 D1 read-vs-guard refinement** held: the 4 admin/role-guarded config functions were correctly
  INLINE_GUARD_REFUTED (no false unblock), and the one value-flow function reached READY.
- The Tier-C PoC convention (verbatim control-flow + minimal mocks + reference/bug/control tests) proved the mechanism
  without the full import closure.

## Honest limits (not overstated)
- **1 STRONG, not EXACT**: H-01's awarded framing is heartbeat-deviation arbitrage; the PoC proved the underlying
  staleness-consumption primitive (same root cause + locus). Graded STRONG conservatively.
- **Residual gaps** (informative, not this run's binding constraint): RECALL_GAP on `getRSETHPrice` (H-03 missed); the
  current evidence layer does not model check-effect ordering (H-02), strategy-update accounting (M-01), or design-absence
  slippage (M-02) — those candidates surfaced/queued but did not reach READY.
- Single fresh target — one data point. A second blind target would raise confidence.

## Production authority
**WITHHELD.** Blind-eval/advisory only; no submission/severity/confirmed; Tier-C faithful reproduction.

## Next
The arc generalized (verdict A). Options: (1) a second fresh blind target for confidence; (2) repair the named residual
gaps (recall for inflation/donation loci like getRSETHPrice; evidence lenses for ordering / accounting / slippage) then
re-blind. Promotion to production remains a separate human decision.
