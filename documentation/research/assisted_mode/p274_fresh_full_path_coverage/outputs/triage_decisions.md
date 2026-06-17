# Impact-first PoC triage — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| id | subsystem | impact_class | fit | recall-Δ | feasibility | heavy | outcome |
|---|---|---|---|---|---|---|---|
| distribute | liquidation | cross_domain_accounting_mismatch | 13 | Y | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| wq_withdraw | withdrawal_queue | systemic_liveness_failure | 11 | Y | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| burnAndWithdraw | uservault | statemachine_terminal_failure | 11 | Y | moderate | - | **SELECT_FOR_FULL_POC** |
| offers | loan_offers | cross_domain_accounting_mismatch | 11 | - | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| pool_redeem | pool_shares | dust_rounding | 2 | - | easy | - | **DEFER_LOW_IMPACT** |
