# Impact-first PoC triage — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| id | subsystem | impact_class | fit | recall-Δ | feasibility | heavy | outcome |
|---|---|---|---|---|---|---|---|
| health_zero_unliquidatable | liquidation_baddebt | bad_debt | 16 | Y | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| coll_credit_miscalc | collateral_credit | insolvency | 16 | Y | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| liq_incentive_cap_order | liquidation_incentive | liq_redemption_blockage | 15 | Y | moderate | - | **SELECT_FOR_FULL_POC** |
| harvest_drama | rewards | insolvency | 14 | Y | easy | - | **DEFER_LOW_IMPACT** |
| liq_incentive_revert | liquidation_incentive | griefing_minor | 5 | - | easy | - | **KEEP_AS_CONTROL** |
| coll_credit_dust | collateral_credit | dust_rounding | 3 | - | easy | - | **KEEP_AS_CONTROL** |
