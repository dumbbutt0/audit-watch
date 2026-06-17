# badger-2024-06-holdout — FROZEN CANDIDATES (blind, pre-reveal)

Architecture: eBTC — Liquity-fork BTC CDP/lending (BorrowerOperations, CdpManager(Storage),
LiquidationLibrary, ActivePool, PriceFeed/ChainlinkAdapter/Tellor, SortedCdps, EBTCToken, LeverageMacro).
Heavily pre-audited (multiple prior audits + echidna invariants in scope). Sealed-key hash 05ee0ed459a96c16
(not opened).

## DELIBERATE COVERAGE-BOUND DATAPOINT
722 critical in-scope items / 21k LOC. Under P245 full-read enforcement this contest is **NOT fully
readable in one pass → the gate BLOCKS triage (coverage incomplete)**. Per the approved plan, badger is the
explicit "large contest under the gate" datapoint: I performed a focused genuine read of the **oracle layer
only** (ChainlinkAdapter; PriceFeed/Tellor skim) — ~1% of critical surface. Recall here is expected to be
coverage-bound; this is recorded honestly, not inflated. Advisory lenses: 0.

## Candidates (oracle layer only)
| id | sev | locus | mechanism |
|---|---|---|---|
| B-M1 | Medium | ChainlinkAdapter._getRoundData (PREVIOUS_ROUND) | previous round fetched via `getRoundData(latestRoundId - 1)` assumes sequential round IDs; Chainlink round IDs encode `phaseId<<64 \| aggrRoundId`, so `-1` across a phase boundary returns a wrong/stale round or reverts → incorrect previous price / DoS. |
| B-M2 | Medium | ChainlinkAdapter._latestRoundData / _getRoundData | validates `answer > 0` and `feedRoundId > 0` but performs NO staleness (`updatedAt`/heartbeat) or `answeredInRound >= roundId` check at the adapter level; freshness depends entirely on PriceFeed (not fully verified here). |

## Gate / proof status
P245 gate: **BLOCK** (coverage incomplete — ~1% critical read; the gate correctly refuses triage on an
unread 722-item surface). Proof: BLOCKED_BY_BUILD. This contest primarily measures the gate's correct
refusal behavior on an oversized target, not full hunting.
FREEZE: final pre-reveal.
