# P275 — COVERAGE_ROUTER_OUTPUTS (Phase 4, frozen P273)

Frozen `award_class_coverage_router.py` (`b87e3d22d1fb915b`) over the 6 surfaced loci with BLIND class signals
(`outputs/coverage_candidates.json`). Output `outputs/coverage_decisions.json` (`1049da0ea47dcdd4`). Guard: **0
violations**.

## Routing (handoff to P269)
| rep | award_class | sig | recall-Δ | label |
|---|---|---|---|---|
| `migrate` | STATE_MACHINE_LIFECYCLE | 2 | – | **COVERAGE_SELECT** |
| `npm_mint` | ACCESS_CONTROL_AUTHORIZATION | 3 | – | **COVERAGE_SELECT** |
| `swap_callback` | ORDER_VALIDATION | 2 | – | **COVERAGE_SELECT** |
| `pool_mint` | SHARE_ROUNDING_PRECISION | 2 | Y | **COVERAGE_SELECT** |
| `pool_burn` | SHARE_ROUNDING_PRECISION | 2 | Y | (dup class) |
| `beacon_constructor` | EXTERNAL_INTEGRATION | 2 | Y | **COVERAGE_DEFER_LOW_SIGNAL** |

`handoff_queue_to_p269 = [migrate, npm_mint, swap_callback, pool_mint, pool_burn]` — **4 distinct classes**
(STATE, ACCESS, ORDER, SHARE).

## Reading (the diversity test)
- **4 classes routed, no monoculture.** Both anti-monoculture guard classes present — **ACCESS** (`npm_mint`) and
  **ORDER** (`swap_callback`) each got a representative. SHARE represented by `pool_mint`/`pool_burn`. STATE by
  `migrate`.
- `beacon_constructor` correctly DEFER_LOW_SIGNAL (`impact_supported:false`, trivial OZ pass-through) — anti-drama held.
- This mirrors the P274 result: the coverage layer spreads representation across classes rather than letting one
  consume the queue. Here the spread is over a *different* class mix (DEX/AMM rather than lending), confirming the
  router is not gondi-specific.

Next: Phase 5 — frozen P269 impact-first triage.
