# P131 — Recall Measurement

## Objective measure (deep-pass visibility vs awarded yardstick)
The boost-delta is **deep-pass-only ON** (these 70 functions are sub-cutoff OFF → routed to cheap-sweep, which
is clear-biased, not bug-hunting). So awarded functions in the delta are recoverable ON and effectively lost OFF.

| | OFF | ON |
|---|---|---|
| awarded functions deep-pass-visible | 6/19 (32%) | **14/19 (74%)** |
| → recall ceiling lift | — | **+8 functions / +42 pp** |

The +8: `NoyaValueOracle._getValue`, `ChainlinkOracleConnector.getValue`, `BalancerConnector._getPositionTVL`,
`BalancerConnector.totalLpBalanceOf`, `AerodromeConnector._getPositionTVL`, `MorphoBlueConnector._getPositionTVL`,
`PendleConnector._getPositionTVL`, `SiloConnector._getPositionTVL`.

## Qualified recall (does visibility convert to a finding?)
Visibility is **necessary but not sufficient**. From source review (see `specialist_findings.md`), all 8 sit in
the `value_exit`/oracle surface and are substantively reviewable; 3 assessed HIGH discoverability (Balancer
spot-TVL, Chainlink staleness, NoyaValueOracle chaining), the rest MED-HIGH (same spot-TVL class). So the
realistic recovered-recall is **most of the +8**, conditional on the specialist actually confirming each — which
a full human-graded run (next phase) would quantify.

## What the boost cannot recover (honest ceiling)
5 awarded functions remain uncovered ON: `SNXConnector._getPositionTVL` (**absent** from the manifest —
enumeration/scope-membership gap), `OmnichainManagerBaseChain.updateTVL` (no risk tag → gate correctly inert),
and others outside the ranking lever. These need a different fix (enumeration/scope, or callgraph reachability),
not the P130 boost.

## Tie-back to P130 / P129
This confirms the P130 candidate-coverage gain (32%→74%) translates into **genuinely reviewable bug surface**,
directly attacking the P129 dominant miss class ("risk-bearing helper logic ranked below the cutoff →
wrong/under-inspected contract"). The recall improvement is real at the stage P129 identified as the bottleneck.
