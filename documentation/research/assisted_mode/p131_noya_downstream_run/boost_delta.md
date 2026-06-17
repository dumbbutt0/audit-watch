# P131 — Boost-Delta (noya, real scope)

Deterministic A/B, identical `--contract`, only `library_internal_surface_boost` toggled. Both manifests use
noya's real `scope.txt` (377 in-scope functions).

## A/B summary (function-level, via P130 `measure.py`)
| Metric | OFF | ON | Δ |
|---|---|---|---|
| awarded-FUNCTION deep-pass coverage | 6/19 (32%) | **14/19 (74%)** | **+8 fns / +42 pp** |
| awarded-CONTRACT deep-pass coverage | 17/19 (89%) | 18/19 (95%) | +1 |
| internal/private fns scoring ≥3 | 2/205 (1%) | 13/205 (6%) | +11 |
| high-surface in-scope functions (volume) | 158 | 228 | **+70 (+44%)** |
| functions boosted (`surface_boost`) | 0 | 70 | +70 |

## Boost-delta composition (the 70 lifted functions)
- visibility: **public 56**, internal 11, external 3
- mutability: **view 58**, "" 7, pure 5 → overwhelmingly **read/value-computation helpers**, as designed.
- spread across connectors + registry/accounting (cap 3/contract holds).

## Recall arm — awarded functions newly surfaced by the boost (deep-pass-only ON)
8 distinct awarded functions (10 entries incl. overloads) move from sub-cutoff (OFF, cheap-sweep) to deep-pass
(ON). All carry mechanism_class `value_exit` / oracle:
`NoyaValueOracle._getValue` (H-03), `ChainlinkOracleConnector.getValue` (H-01),
`BalancerConnector._getPositionTVL` + `totalLpBalanceOf` (H-13/14),
`AerodromeConnector._getPositionTVL` (H-06), `MorphoBlueConnector._getPositionTVL` (H-19),
`PendleConnector._getPositionTVL` (H-05/07), `SiloConnector._getPositionTVL` (H-15).

The 5 still-uncovered awarded functions are out of P130's reach: `SNXConnector._getPositionTVL` (**absent**
from manifest — enumeration/scope gap), `OmnichainManagerBaseChain.updateTVL` (no risk tag → gate correctly
doesn't fire), and a few others — none are ranking misses the boost could address.

Artifacts: `noya_OFF.json`, `noya_ON.json`, `boost_delta_set.json`, `nonawarded_boosted.json`.
