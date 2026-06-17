# P133 — Recall Grade (8 boost-delta awarded functions)

Informed-reviewer grade vs the specific answer-key bug. HIT = surfaces the exact awarded mechanism;
PARTIAL = right function + identifiable issue but mechanism needs cross-function/protocol depth; MISS = visible
but a specialist review would not reliably reach the mechanism. (HIT/PARTIAL are upper bounds — see method.md.)

| Awarded | Fn | Answer-key root cause | Source signal | Grade |
|---|---|---|---|---|
| H-19 | `MorphoBlueConnector._getPositionTVL` | TVL calc error | `supplyAmount + borrowAmount + collateral` — **adds debt instead of subtracting** (sibling `SiloConnector` correctly does `deposit − borrow`) → visible sign error | **HIT** |
| H-03 | `NoyaValueOracle._getValue` | loop reuses static `asset` not `quotingToken` | loop sets `quotingToken=sources[i]` but passes `asset` each hop → dead-variable/logic smell visible in the 12-line loop | **HIT** |
| H-06 | `AerodromeConnector._getPositionTVL` | omits gauge-staked LP | counts only `IERC20(pool).balanceOf(this)`; omission found via deposit-path/TVL conservation cross-check | **PARTIAL** |
| H-15 | `SiloConnector._getPositionTVL` | composition wrong | `balanceOf` of Silo collateral/debt **share** tokens used as underlying (shares-vs-assets); needs Silo depth | **PARTIAL** |
| H-22 | `PendleConnector._getPositionTVL` | composition invalid | right target; exact SY/PT/YT/LP composition error needs Pendle SY-rate depth | **PARTIAL** |
| H-13 | `BalancerConnector._getPositionTVL` | ÷weight twice → undervalue | subtle single-token weighted-pool extrapolation; looks plausible (answer key predicts MISS) | **MISS** |
| H-14 | `BalancerConnector.totalLpBalanceOf` | staked vs held composition | counts held + aura-staked; subtle composition error not surface-visible | **MISS** |
| H-01 | `ChainlinkOracleConnector.getValue` | ETH/USD 18-dec vs 8-dec → 1e10 multi-hop | subtle decimals/units bug across multi-hop routing (answer key predicts MISS) | **MISS** |

## Tally
- **HIT 2 · PARTIAL 3 · MISS 3** (of 8 boost-delta awarded).
- **Useful recall = (HIT+PARTIAL) = 5/8 = 62%** of the visible awarded functions.
- **Strict recall = HIT = 2/8 = 25%.**
- **Visibility ceiling (P130/P132) = 8/8** → **deep-reasoning gap = 3/8 visible-but-MISS** (subtle weighted-pool
  math + oracle decimals).

## Alignment with the answer key's own hypothesis
The answer key predicted: TVL omission/composition bugs (Aerodrome/Silo/Pendle) surfaceable, but subtle ones
(H-13 single ÷, oracle H-01/H-03) MISS. My grade matches closely (Aerodrome/Silo/Pendle = PARTIAL/HIT; H-13 +
H-01 = MISS), with two refinements: H-19 Morpho is a **HIT** (the add-vs-subtract sign error is more visible than
generic "TVL calc"), and H-03 NoyaValueOracle is a **HIT** (the loop-variable misuse is a visible logic smell,
more catchable than a pure decimals bug).

## Interpretation
The P130 boost is **necessary** (without it all 8 sit at score 2 in clear-biased cheap-sweep → 0 recall) but
**not sufficient**: visibility converts to ~62% useful detection by an informed specialist, with 3/8 requiring a
deeper mechanism pass (weighted-pool math, multi-hop decimals). Recall is real and boost-attributable, but
**depth-bound**.
