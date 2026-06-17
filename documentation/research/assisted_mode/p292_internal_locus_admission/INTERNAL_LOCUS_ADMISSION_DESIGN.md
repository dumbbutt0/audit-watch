# P292 — INTERNAL_LOCUS_ADMISSION_DESIGN

## P291 diagnosis (recall fixed, admission failed)
P291's harness expansion surfaces internal accounting/reward loci (e.g. `StakingRewards._increaseUserShare`) at the
advisory layer. But the queue is built from `cov.handoff_queue_to_p269`, and the P273 router already labeled the locus
`COVERAGE_DEFER_DUPLICATE_CLASS` (its SHARE_ROUNDING slot was filled) → it never enters the queue → Lens 3 never sees it.
The failure is ADMISSION, not recall.

## Why the queue, not the router
The router INPUT (built by the non-editable `p276_corpus_replay`) carries no `internal_locus` flag, so the router cannot
cleanly know it; and the router is pinned across ~22 tests. The queue (`expanded_validation_queue.build`) already loads
BOTH the shadow file (`internal_locus`/`reached_from_public_entry`/`source_span`/`call_path`) AND the full coverage
decisions (every candidate's `award_class` + DEFER `label`). So the exception lives in the queue; the router stays
byte-identical.

## The exception (narrow, fail-closed)
After the base handoff queue, for each coverage decision with `label==COVERAGE_DEFER_DUPLICATE_CLASS`, ADMIT iff ALL:
shadow `internal_locus==true` · `reached_from_public_entry` present · `source_span` present · distinct function from the
already-admitted same-class candidate · `award_class ∈ {REWARDS_CLAIMS, SHARE_ROUNDING_PRECISION,
ACCOUNTING_LIQUIDATION_BAD_DEBT, STATE_MACHINE_LIFECYCLE, ORACLE_PRICING}` · ≥1 internal-locus signal term · caps not
exceeded. Default dedup for NON-internal duplicates is untouched (they stay DEFERRED_DUPLICATE_CLASS).

## Caps + anti-monoculture
`max_same_class_admissions=2`, `max_total_admissions=5`; admissions are a SEPARATE bounded pool appended on top of the
base `validation_queue_budget` (no eviction). Anti-monoculture re-checked on the COMBINED queue: an admission pushing a
class >40% → `DEFERRED_MONOCULTURE_GUARD` unless queue<5 or <3 classes.

## Ranking (deterministic; no award/target signals)
Deferred internal loci ranked by class-relevant term count + reached-from-an-already-queued entry, then id. NEVER uses
award titles/bodies/IDs/reveal/target names.

## Decisions emitted
`duplicate_class_decision ∈ {ADMITTED_PRIMARY_CLASS, DEFERRED_DUPLICATE_CLASS, ADMITTED_INTERNAL_LOCUS_EXCEPTION,
DEFERRED_INTERNAL_LOCUS_CAP, DEFERRED_MONOCULTURE_GUARD}` + reason/competing/reached_from/call_path/cap_status.

## FP/noise controls + not scaleout
Bounded (≤5/contest), advisory-only, fail-closed eligibility, default dedup preserved, anti-monoculture enforced. This is
a targeted admission fix for distinct internal loci — NOT a breadth/scaleout change.
