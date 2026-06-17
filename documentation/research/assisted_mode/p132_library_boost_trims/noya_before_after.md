# P132 — Noya Before/After (real scope, boost ON)

Identical `--contract` invocation; the only difference is the two trims now active in boost eligibility.
Pre-trim = P131 `noya_ON.json`; post-trim = `noya_ON_trimmed.json`.

| Metric | Before trim (P131) | After trim (P132) | Δ |
|---|---|---|---|
| boosted functions (distinct) | 67 | 60 | **−7** |
| — mock boosts removed | — | — | **3** (`ConnectorMock2.*`) |
| — trivial boosts removed | — | — | **4** |
| **awarded boosted functions** | **8** | **8** | **0 (all preserved)** |
| awarded-FUNCTION deep-pass coverage | 14/19 (74%) | 14/19 (74%) | **0** |
| awarded-CONTRACT deep-pass coverage | 18/19 (95%) | 18/19 (95%) | 0 |
| deep-pass volume (functions ≥3) | 228 | 221 | −7 |

## Exactly what was removed (7)
- **mock (3):** `ConnectorMock2._updateTokenInRegistry`, `ConnectorMock2.getPositionTVL`,
  `ConnectorMock2.getUnderlyingTokens`
- **trivial (4):** `AaveConnector._getUnderlyingTokens`, `CompoundConnector._getUnderlyingTokens`,
  `SNXV3Connector._getUnderlyingTokens` (all `return new address[](0);`), `Watchers.verifyRemoveLiquidity`
  (empty/trivial body)

## All 8 awarded preserved (none lost)
`NoyaValueOracle._getValue`, `ChainlinkOracleConnector.getValue`, `BalancerConnector._getPositionTVL`,
`BalancerConnector.totalLpBalanceOf`, `AerodromeConnector._getPositionTVL`, `MorphoBlueConnector._getPositionTVL`,
`PendleConnector._getPositionTVL`, `SiloConnector._getPositionTVL` — all remain ≥ cutoff. The body-based trivial
rule correctly **kept** sibling `_getUnderlyingTokens` implementations that contain real logic (e.g.
`AerodromeConnector._getUnderlyingTokens`), removing only the empty-array returners.

## Unexpected losses
None. Removed set = exactly the targeted mock + trivial noise; zero awarded loss; recall metrics flat.
