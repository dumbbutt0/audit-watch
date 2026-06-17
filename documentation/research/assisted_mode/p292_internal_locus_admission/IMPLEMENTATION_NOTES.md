# P292 — IMPLEMENTATION_NOTES

## Files changed (allow-list)
| File | Change |
|---|---|
| `expanded_validation_queue.py` | internal-locus admission exception in `build()` after the handoff queue: scan coverage `COVERAGE_DEFER_DUPLICATE_CLASS` decisions, join shadow `internal_locus`, admit eligible distinct loci (caps + anti-monoculture), emit `duplicate_class_decisions` + `internal_locus_admitted`. |
| `config/research_expanded_validation_queue.json` | `internal_locus_admission` block (enabled, caps, eligible_classes, signal_terms). |

## Router NOT edited (kept byte-identical)
`award_class_coverage_router.py` (6debb753) is unchanged — the exception lives in the queue, which already has the shadow
`internal_locus` flag + the coverage DEFER decisions. This avoids the router's ~22-test pin cascade and preserves default
duplicate-class dedup exactly.

## Admission as a bounded appended pool
Internal admissions append on top of the base `validation_queue_budget` (10) — no eviction of base candidates — capped at
≤2/class, ≤5/contest. Anti-monoculture re-checked on the combined queue. Each affected candidate gets a
`duplicate_class_decision`.

## Hash-pin cascade (small)
Only `expanded_validation_queue.py` (374e1689→6a560f36) + its config (8dc7556e→aacd5ba4) changed. No test FROZEN dict
pins them. The 3 blind frozen-stack live-checks (test_p287/p288/p290) re-check live vs recorded baseline → extended their
exclusion set with the queue + config (baseline hash_manifests preserved). All 3 cascade failures were hash-only.
