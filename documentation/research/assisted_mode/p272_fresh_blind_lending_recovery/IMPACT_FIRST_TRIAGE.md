# P272 — IMPACT_FIRST_TRIAGE (Phase 4)

Frozen **P269** triage (`63c88d02d2c7eefa`) over advisory candidates + selector outputs. Input
`p272_triage_input.json` (`c7add0a97047266f`); decisions `p272_triage_decisions.json` (`fdc66756bc51107f`); guard
PASS. **selected_count = 3.**

| candidate | subsystem | impact_class | fit | heavy | outcome |
|---|---|---|---|---|---|
| **health_zero_unliquidatable** | liquidation_baddebt | bad_debt | 16 | **Y** | **SELECT_FOR_PARTIAL_RUNTIME** |
| **coll_credit_miscalc** | collateral_credit | insolvency | 16 | **Y** | **SELECT_FOR_PARTIAL_RUNTIME** |
| **liq_incentive_cap_order** | liquidation_incentive | liq_redemption_blockage | 15 | - | **SELECT_FOR_FULL_POC** |
| harvest_drama | rewards | insolvency (unsupported) | 14 | - | DEFER_LOW_IMPACT |
| liq_incentive_revert | liquidation_incentive | griefing_minor | 5 | - | KEEP_AS_CONTROL |
| coll_credit_dust | collateral_credit | dust_rounding | 3 | - | KEEP_AS_CONTROL |

Three high-impact award-class lending subsystems routed (liquidation-incentive full-PoC; bad-debt + collateral-credit
partial-runtime, heavy not de-scoped); unsupported drama deferred; easy rivals controls. `liq_incentive_cap_order` is
FULL_POC-feasible (near-pure formula) → the primary runtime PoC target. Frozen before completion.
