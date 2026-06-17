# P275 — BASE_AND_HARNESS_FREEZE (Phase 1)

Frozen BEFORE dashboard/selector/coverage/triage/completion and any answer-key access. Deterministic; no API/answer
key. ronin source isolated at `/tmp/p275_fresh/ronin` (submodules pinned `03c8017` / `27f9d28`).

## Harness result
**21,954 manifest functions · 343 in-scope · 38 checkpoint-hit · 6 advisory candidates · guard PASS (0 violations).**
Frozen version hashes in metrics: P260 `d6b494bc3c0cc746` · P262 `a48336275cb65a4f` · harness_config
`e9b74687793fd110`.

## Advisory candidates (rank = prioritizer score)
| rank | locus | templates | class signal (blind) |
|---|---|---|---|
| 1.0 | `V3Migrator.migrate` | T1,T4,T9 | STATE/migration + external-dep + math |
| 3.0 | `NonfungiblePositionManager.mint` | T8 | STATE/position lifecycle |
| 4.0 | `V3SwapRouter.katanaV3SwapCallback` | T3 | ORDER/front-run + external callback |
| 6.0 | `KatanaV3Pool.mint` | T8 | SHARE/math (concentrated liquidity) |
| 8.0 | `KatanaV3Pool.burn` | T2 | SHARE/math + accounting |
| 10.0 | `KatanaV3PoolBeacon.constructor` | T4 | UPGRADE/state |

## Narrow baseline (rank < 5) vs recall-delta (rank ≥ 6)
- **Narrow top-5:** `V3Migrator.migrate` (1) · `NonfungiblePositionManager.mint` (3) · `V3SwapRouter.katanaV3SwapCallback` (4).
- **Recall-delta:** `KatanaV3Pool.mint` (6) · `KatanaV3Pool.burn` (8) · `KatanaV3PoolBeacon.constructor` (10).
- recall-delta fraction = 3/6 = 0.50.

## Class spread of the candidate pool (blind)
STATE/migration (`V3Migrator`) · position lifecycle (`NPM.mint`) · ORDER/front-run (`V3SwapRouter` callback) ·
SHARE/AMM-math (`KatanaV3Pool.mint/burn`) · UPGRADE (`Beacon.constructor`) — ≥2 distinct plausible classes.

## ⚠ Recall-depth note (carried into diagnosis)
**No `KatanaGovernance`/authorization candidate surfaced**, despite governance being a large in-scope contract (37
items) and access-control being a plausible award class. The checkpoint-driven harness (accounting + state-transition)
did not trip on the authorization surface. If awarded mechanisms cluster in governance, this is a **RECALL_GAP** risk —
recorded now, pre-reveal.

## Freeze hashes (sha256[:16])
| artifact | hash |
|---|---|
| ronin_coverage_manifest.json | `38902e1f5e546ffb` |
| ronin_accounting_checkpoint.json | `93595188c329d3cd` |
| ronin_state_transition_checkpoint.json | `6f37aa966435997e` |
| ronin_shadow/recall_advisory_candidates.json | `61ef91edb391435f` |
| ronin_shadow/recall_metrics.json | `0b5057d24e24f1db` |

No answer key consulted. Next: Phase 2 advisory dashboard.
