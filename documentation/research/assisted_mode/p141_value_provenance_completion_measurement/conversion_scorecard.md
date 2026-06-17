# P141 — Conversion Scorecard

## Per-architecture
| Arch | queued | completed | pending | accepted | rejected | finding | likely_exp | needs_human | strong_clear | error | clean strong_clear | clean false finding | buggy-useful | render OK | confirmed Δ | Validated Δ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| noya | 2 | 2 | 0 | 2 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 1/1 | ✓ | 0 | 0 |
| blackhole | 3 | 3 | 0 | 3 | 0 | 1 | 0 | 0 | 2 | 0 | 2 | 0 | 1/1 | ✓ | 0 | 0 |
| size | 2 | 2 | 0 | 2 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 1/1 | ✓ | 0 | 0 |
| **TOTAL** | **7** | **7** | **0** | **7** | **0** | **2** | **0** | **1** | **4** | **0** | **4** | **0** | **3/3** | **✓** | **0** | **0** |

## Decision distribution (7 completed)
- finding: **2** (NoyaValueOracle._getValue, RewardsDistributor.claim_many)
- likely_exploitable: **0**
- needs_human: **1** (SellCreditMarket.validateSellCreditMarket)
- strong_clear: **4** (SolvencyV2, RewardsDistributor.claim, RewardsDistributor.claimable, AccountingLibrary…)
- error: **0**

## Safety-critical rates
- **clean false-finding rate = 0/4 = 0%** (all 4 clean controls cleared — incl. the fresh SolvencyV2 and the
  HIGH-confidence blackhole C1). Matches P138's 0/5.
- **rejected/quarantined = 0/7** (no unsafe artifact).
- **buggy-useful = 3/3** on the buggy items present (2 finding + 1 needs_human; B4 is "useful uncertainty").
- **confirmed-count change = 0** and **Validated-Findings change = 0** on every architecture (hard requirement).

## Prompt-derived vs runtime-confirmed
- prompt-derived advisory: **7/7**.
- runtime-confirmed: **0/7** (no PoC executed; findings remain hypotheses pending PoC + human review).

## Cross-architecture conclusion
The completion loop behaves identically across three architectures (noya / blackhole / size): all queued jobs
ingest, render advisory-only, preserve the triplet, and leave confirmed/Validated untouched, with **zero clean
false findings** and zero unsafe promotions.
