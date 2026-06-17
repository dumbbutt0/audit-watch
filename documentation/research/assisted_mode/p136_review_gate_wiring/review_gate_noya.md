# Audit Review Gate — noya-2024-04-eval
Generated: 2026-06-04T17:26:10.089572+00:00
Target: NOYA (Code4rena Eval)

---

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Info | 0 |

---

## Validated Findings

| ID | Title | Severity | Entry Point | ICE_C | ICE_E |
|---|---|---|---|---|---|

---

## Finding Details


---

## Advisory Context — NOT confirmed (mechanism detectors)

> **Advisory only — NOT confirmed findings, NOT submission-ready.** Every row below is `advisory_only=true`, `submission_ready=false`, `requires_human_review=true`. These are existing mechanism-detector signals surfaced for human review only; they are **excluded from the Validated Findings table and the confirmed-findings count**. Do not submit or assign severity from this section without independent human/PoC confirmation.

| Detector | Status | Location | Mechanism | Confidence | Route reason |
|---|---|---|---|---|---|
| connector_position_accounting | advisory | `AaveConnector._getPositionTVL` | external_reader_aggregate | high | mechanism layer (connector_position_accounting/advisory) flagged this surface; the surface |
| connector_position_accounting | advisory | `MorphoBlueConnector._getPositionTVL` | external_reader_aggregate | high | mechanism layer (connector_position_accounting/advisory) flagged this surface; the surface |
| units_invariant | report_only | `AccountingManager.calculateDepositShares` | assumed_18_decimals | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| units_invariant | report_only | `AccountingManager.executeDeposit` | assumed_18_decimals | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| units_invariant | report_only | `AccountingManager.totalAssets` | shares_assets | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| units_invariant | report_only | `BalancerConnector.totalLpBalanceOf` | shares_assets | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| units_invariant | report_only | `FraxConnector.verifyHealthFactor` | price_per_share | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| units_invariant | report_only | `FraxConnector._getHealthFactor` | price_per_share | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| units_invariant | report_only | `PendleConnector._getPositionTVL` | price_per_share | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| units_invariant | report_only | `ChainlinkOracleConnector.getValue` | chainlink_decimals | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| units_invariant | report_only | `ChainlinkOracleConnector.getValueFromChainlinkFeed` | chainlink_decimals | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| units_invariant | report_only | `WETH_Oracle.latestRoundData` | chainlink_decimals | high | mechanism layer (units_invariant/report_only) flagged this surface; the surface specialist |
| connector_position_accounting | advisory | `PositionRegistry.updateHoldingPosition` | registry_key_mismatch | medium | mechanism layer (connector_position_accounting/advisory) flagged this surface; the surface |
| connector_position_accounting | advisory | `AerodromeConnector._getPositionTVL` | external_reader_aggregate | medium | mechanism layer (connector_position_accounting/advisory) flagged this surface; the surface |
| connector_position_accounting | advisory | `BalancerConnector._getPositionTVL` | position_tvl_product_div | medium | mechanism layer (connector_position_accounting/advisory) flagged this surface; the surface |
| connector_position_accounting | advisory | `CamelotConnector._getPositionTVL` | external_reader_aggregate | medium | mechanism layer (connector_position_accounting/advisory) flagged this surface; the surface |
| connector_position_accounting | advisory | `SNXV3Connector._getPositionTVL` | external_reader_aggregate | medium | mechanism layer (connector_position_accounting/advisory) flagged this surface; the surface |
| arithmetic_conservation | advisory | `AccountingManager.fulfillCurrentWithdrawGroup` | supply_aggregate | medium | mechanism layer (arithmetic_conservation/advisory) flagged this surface; the surface speci |
| arithmetic_conservation | advisory | `AccountingManager.neededAssetsForWithdraw` | supply_aggregate | medium | mechanism layer (arithmetic_conservation/advisory) flagged this surface; the surface speci |
| arithmetic_conservation | advisory | `AccountingManager.TVL` | supply_aggregate | medium | mechanism layer (arithmetic_conservation/advisory) flagged this surface; the surface speci |
| arithmetic_conservation | advisory | `AerodromeConnector._getPositionTVL` | supply_aggregate | medium | mechanism layer (arithmetic_conservation/advisory) flagged this surface; the surface speci |
| arithmetic_conservation | advisory | `BalancerConnector.totalLpBalanceOf` | supply_aggregate | medium | mechanism layer (arithmetic_conservation/advisory) flagged this surface; the surface speci |
| arithmetic_conservation | advisory | `PendleConnector._getPositionTVL` | supply_aggregate | medium | mechanism layer (arithmetic_conservation/advisory) flagged this surface; the surface speci |
| arithmetic_conservation | advisory | `SiloConnector._getPositionTVL` | supply_aggregate | medium | mechanism layer (arithmetic_conservation/advisory) flagged this surface; the surface speci |
| arithmetic_conservation | advisory | `SolvencyV2.getUserCollateralAmount` | supply_aggregate | medium | mechanism layer (arithmetic_conservation/advisory) flagged this surface; the surface speci |
| arithmetic_conservation | advisory | `LifiImplementation.performSwapAction` | supply_aggregate | medium | mechanism layer (arithmetic_conservation/advisory) flagged this surface; the surface speci |

### Deep-pass recommendations (review_context only)

| Location | Recommended prompt | Reason |
|---|---|---|
| `SolvencyV2.convertAmountsToValues` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
| `OracleLibrary.getWeightedArithmeticMeanTick` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
| `OracleLibrary.getChainedPrice` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
| `NoyaValueOracle.updateDefaultPriceSource` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
| `NoyaValueOracle.updateAssetPriceSource` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
| `NoyaValueOracle._getValue` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
| `ChainlinkOracleConnector.setAssetSources` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
| `AccountingManager.calculateDepositShares` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
| `AccountingManager.executeDeposit` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
| `AccountingManager.calculateWithdrawShares` | deep_pass_value_provenance | multi-hop oracle/value loop / loop-carried quote/asset/value variable — run deep_pass_valu |
