# P134 — P133 Target Matrix (measurement only)

The 8 noya boost-delta awarded functions, with P133 surface-specialist labels and mechanism class. Used only to
score detector recovery — never to tune detector logic.

| Awarded | Contract.function | P133 label | Mechanism class (answer key) | Expected detector(s) |
|---|---|---|---|---|
| H-03 | NoyaValueOracle._getValue | HIT | oracle multi-hop loop reuses `asset` not `quotingToken` (logic) | (logic — none obvious) |
| H-01 | ChainlinkOracleConnector.getValue | MISS | oracle decimals 18 vs 8 → 1e10 multi-hop | units_invariant (chainlink_decimals) |
| H-13 | BalancerConnector._getPositionTVL | MISS | ÷weight twice (weighted-pool math) | connector_position_accounting (Shape B) |
| H-14 | BalancerConnector.totalLpBalanceOf | MISS | staked vs held LP composition | arithmetic_conservation / units (shares_assets) |
| H-06 | AerodromeConnector._getPositionTVL | PARTIAL | omits gauge-staked LP | semantic_tvl_completeness (omission) |
| H-19 | MorphoBlueConnector._getPositionTVL | HIT | adds debt instead of subtracting | connector_position_accounting (Shape A) / semantic_tvl |
| H-22 | PendleConnector._getPositionTVL | PARTIAL | SY/PT/YT composition invalid | arithmetic_conservation / units |
| H-15 | SiloConnector._getPositionTVL | PARTIAL | composition (shares-vs-assets) | arithmetic_conservation / semantic_tvl |

Non-awarded boosted functions (52 from P133) = noise/control sample for off-target flag counting.
