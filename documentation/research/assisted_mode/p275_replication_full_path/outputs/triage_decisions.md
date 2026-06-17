# Impact-first PoC triage — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| id | subsystem | impact_class | fit | recall-Δ | feasibility | heavy | outcome |
|---|---|---|---|---|---|---|---|
| pool_mint | pool | cross_domain_accounting_mismatch | 13 | Y | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| npm_mint | governance_auth | cross_domain_accounting_mismatch | 11 | - | moderate | - | **SELECT_FOR_FULL_POC** |
| swap_callback | router | cross_domain_accounting_mismatch | 11 | - | moderate | - | **SELECT_FOR_FULL_POC** |
| pool_burn | pool | local_misprice | 5 | Y | moderate | - | **DEFER_LOW_IMPACT** |
| migrate | migrator | local_misprice | 3 | - | easy | - | **KEEP_AS_CONTROL** |
