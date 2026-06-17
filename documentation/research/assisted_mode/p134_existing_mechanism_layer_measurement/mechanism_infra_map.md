# P134 — Mechanism Infrastructure Map

All five are **read-time** detectors (manifest + source-snippet) → **no Slither / no compilation needed**; all
ran on noya cleanly.

| Detector | Files | Output | Status | Target mechanism | Wired? | Review-safe? |
|---|---|---|---|---|---|---|
| connector_position_accounting | `scripts/connector_position_accounting_{taxonomy,audit}.py`, `config/connector_position_accounting_patterns.json` | `output/connector_position_accounting_audit.json` | **advisory** (routes via `advisory_escalation_gate`, strict-full-audit only) | Shape A external_reader_aggregate (debt/supply mix), Shape B position_tvl_product_div (÷weight), Shape C registry key mismatch | yes (advisory) | yes |
| arithmetic_conservation | `scripts/arithmetic_conservation_{taxonomy,audit}.py`, `config/arithmetic_conservation_patterns.json` | `output/arithmetic_conservation_audit.json` | **advisory** (advisory_escalation_gate, strict-full-audit only) | supply_aggregate (≥2-term balance/supply aggregate), invariant_rounding | yes (advisory) | yes |
| units_invariant | `scripts/units_invariant_{taxonomy,audit}.py`, `config/units_invariant_patterns.json`, `prompts/units_invariant_review.md` | `output/units_invariant_audit.json` | **report-only** (NOT surfaced to review/routing) | 24 categories incl. chainlink_decimals, oracle_price_decimals, shares_assets, price_per_share | **no (report only)** | yes |
| semantic_tvl_completeness | `scripts/semantic_tvl_completeness_{taxonomy,audit}.py` | `output/semantic_tvl_completeness_audit.json` | **research-only / un-wired** (is_gate:false, research_only:true, routes_in_production:false) | omitted_external_stake_balance, collateral_debt_side_omission, position_manager_ownership_assumption | **no (research-only)** | yes |
| registry_position_lifecycle | `scripts/registry_position_lifecycle_{taxonomy,audit}.py`, `config/registry_position_lifecycle_patterns.json` | `output/registry_position_lifecycle_audit.json` | **research-only** (research-stable) | missing_registry_update, unguarded_registry_remove | **no (research-only)** | yes |

Inputs: each reads `coverage_manifest.json` (`--manifest`) + the source file/span per item. Outputs carry their
status flags; the research-only ones carry `is_gate:false / research_only:true / routes_in_production:false /
routed_manifest_ids:[]`.

**Key feasibility fact:** none required Slither or noya compilation; all 5 ran read-time on the committed noya
manifest. So the P131-noted Slither block does **not** affect the mechanism layer.
