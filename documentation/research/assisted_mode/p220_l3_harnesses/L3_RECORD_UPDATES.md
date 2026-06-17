# P220 — L3 record updates

Three records rewritten from run artifacts only (schema-valid; `dependency_mocks` from the enum, not the old
`not_built`; every populated field traces to a harness file + run log). `production_source_modified:false`,
`research_only:true`, `routes_in_production:false` on all. `high_promotion_allowed`/`calibrated_severity` are left to
`decide()` at sync time — not written into the record. The P214 DoS carve-out 10 criteria are deliberately **not**
authored (absent → flag-off behavior preserved → no unearned High upgrade).

## Before → after
| field | ZETA-04 | ZETA-10 | ZETA-11 |
|-------|---------|---------|---------|
| l3_status | NEEDS_HARNESS → **PASS** | NEEDS_HARNESS → **FAIL** | NEEDS_HARNESS → **PASS** |
| poc_tier | STATIC_ONLY → **L3_REAL_CONTRACT_POC** | STATIC_ONLY → **L3_REAL_CONTRACT_POC** | STATIC_ONLY → **L3_REAL_CONTRACT_POC** |
| poc_path | "" → ZETA04_pauseBypass.t.sol | "" → ZETA10_reentrancy.t.sol | "" → ZETA11_trident.t.sol |
| actual_delta | "" → mint while paused (+100e18) | "" → reentry reachable, net Δ=0 | "" → empty getPools()[0] reverts (Panic 0x32) |
| expected_delta_or_control | "" → onRevert reverts paused, mints unpaused | partial → net worth Δ=0, residual 0 | partial → with-pool routes (1e18) |
| magnitude_basis | "" → executed mint 100e18 vs guarded sibling | "" → eth_gain==zeta_spent; residual 0 | "" → empty reverts vs control returns 1e18 |
| victim_or_protocol_loss | "" → availability of pause control | "" → none realized (pass-through) | "" → DoS of swap path |
| attacker_model | conditional → privileged_only | permissionless (unchanged) | conditional → unknown |
| impact_class | auth_only (unchanged) | theft (unchanged) | theft → **dos** |
| dependency_mocks | not_built → external_only | not_built → external_only | not_built → external_only |

## decide() output (flag-off, verified)
| ID | l3 | impact | calibrated | high_allowed | blocker |
|----|----|--------|-----------|--------------|---------|
| ZETA-04 | PASS | auth_only | medium | false | attacker_model=privileged_only |
| ZETA-10 | FAIL | theft | invalid | false | l3_status=FAIL |
| ZETA-11 | PASS | dos | medium | false | attacker_model=unknown |

All three carry a written `high_promotion_blocker` → the completion guard's "High blocked ⇒ blocker present" rule is
satisfied. None is promoted to High on AI reasoning.
