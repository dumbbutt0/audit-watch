# P134 — Detector Scorecard

Combined mechanism-layer grade per target (best across detectors; **strict: right-function-only = PARTIAL**).

| Awarded | Fn | P133 | Detector grade | Recovering detector / shape | Routing |
|---|---|---|---|---|---|
| H-01 | ChainlinkOracleConnector.getValue | MISS | **DETECTOR_HIT** | units_invariant = `chainlink_decimals` (the exact decimals mechanism) | report-only |
| H-13 | BalancerConnector._getPositionTVL | MISS | **DETECTOR_HIT** | connector_position_accounting = `position_tvl_product_div` (Shape B = ÷weight) | advisory |
| H-06 | AerodromeConnector._getPositionTVL | PARTIAL | **DETECTOR_HIT** | semantic_tvl_completeness = `omitted_external_stake_balance` (the omission) | research-only |
| H-19 | MorphoBlueConnector._getPositionTVL | HIT | **DETECTOR_HIT** | connector_position_accounting `external_reader_aggregate` (high) + semantic `collateral_debt_side_omission` | advisory + research |
| H-14 | BalancerConnector.totalLpBalanceOf | MISS | **DETECTOR_PARTIAL** | arithmetic_conservation `supply_aggregate` + units `shares_assets` (right locus, generic mechanism) | advisory + report-only |
| H-22 | PendleConnector._getPositionTVL | PARTIAL | **DETECTOR_PARTIAL** | arithmetic_conservation `supply_aggregate` + units `price_per_share` | advisory + report-only |
| H-15 | SiloConnector._getPositionTVL | PARTIAL | **DETECTOR_PARTIAL** | arithmetic_conservation `supply_aggregate` + semantic `collateral_debt_side_omission` (wrong mechanism for Silo) | advisory + research |
| H-03 | NoyaValueOracle._getValue | HIT | **DETECTOR_MISS** | none (logic loop-variable bug; not a decimals/aggregate/TVL/omission shape) | — |

## Tallies
- **Mechanism layer: HIT 4 · PARTIAL 3 · MISS 1** → **useful detector recall 7/8 (88%)**, strict 4/8 (50%).
- **vs P133 surface specialist** (useful 5/8, strict 2/8): the mechanism layer **improves both** (+2 useful, +2 strict).
- **P133 MISS recovery: 3/3** (H-01 HIT, H-13 HIT, H-14 PARTIAL) — the deep-reasoning gap is substantially closed.
- **P133 PARTIAL: H-06 upgraded to HIT** (semantic omission); H-22, H-15 stay PARTIAL.
- **Bonus (outside the 8):** registry_position_lifecycle independently recovers **H-23** (`transferBetweenAccounts`,
  missing_registry_update HIT) + **H-18** (`closeBorrowPosition`, unguarded_registry_remove).

## Per-detector contribution & overlap
- **connector_position_accounting** — marquee: H-13 (Shape B, the headline MISS recovery) + H-19 (Shape A). High precision on-target.
- **units_invariant** — H-01 (decimals MISS recovery); broad (45 flags, 39 off-target) but report-only.
- **semantic_tvl_completeness** — H-06 (omission) + debt-side on H-19/H-15; research-only.
- **arithmetic_conservation** — complementary on H-14/H-22/H-15/H-06 as `supply_aggregate` (PARTIAL); it picks up
  the aggregates CPA de-dups away — not redundant, but generic mechanism (locus, not precise error).
- **Overlap/redundancy:** H-06 flagged by 4 detectors, H-13/H-19/H-15 by 2-3 → strong cross-detector overlap on
  the TVL connectors (de-dup logic exists CPA↔AC↔units). High overlap = the class is well-covered.

## Control noise (off-target flags on non-awarded)
CPA 4 · AC 5 · STC 7 · RPL 3 (= the H-18/H-23 bonus + SNXV3.createAccount) · units 39. The on-class
`_getPositionTVL` off-target flags are the same review class as P133's 39 human-queue items (legitimate
targets, not pure noise). units_invariant's 39 is broad but report-only.
