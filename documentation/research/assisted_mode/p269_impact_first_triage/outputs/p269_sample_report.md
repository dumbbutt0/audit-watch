# Impact-first PoC triage — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| id | subsystem | impact_class | fit | recall-Δ | feasibility | heavy | outcome |
|---|---|---|---|---|---|---|---|
| k_slash | native_vault_slashing_snapshot | slashing | 14 | Y | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| k_snapshot | native_vault_slashing_snapshot | snapshot_checkpoint_corruption | 14 | Y | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| k_vault_inflation | erc20_vault | local_misprice | 8 | Y | easy | - | **SELECT_FOR_FULL_POC** |
| k_approval_revert | erc20_vault | griefing_minor | 3 | - | easy | - | **KEEP_AS_CONTROL** |
