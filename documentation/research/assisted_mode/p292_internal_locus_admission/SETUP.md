# P292 — SETUP

**Phase:** P292 — Coverage/Queue Admission for Internal Loci (supervised; very narrow; production authority WITHHELD).
RESEARCH-ONLY · ADVISORY · default-off · fail-closed.

## What this phase is
P291 fixed recall (internal awarded loci are SURFACED) but the failure moved to ADMISSION: the P273 coverage router
defers them as `COVERAGE_DEFER_DUPLICATE_CLASS`, so they never reach the validation queue / Lens 3. P292 adds a narrow
admission exception (queue layer only) that re-admits DISTINCT internal reward/accounting/share/index loci, preserving
default duplicate-class dedup. NOT a recall repair, NOT a global dedup weakening, NOT scaleout.

## Component
- `expanded_validation_queue.py` (+ config): after the normal handoff queue, scan coverage decisions for
  `COVERAGE_DEFER_DUPLICATE_CLASS`, join the shadow `internal_locus` flag, and ADMIT eligible distinct internal loci as a
  separate bounded pool (≤2/class, ≤5 total) with anti-monoculture re-check + `duplicate_class_decision` reporting.
  **The P273 router is NOT edited** (it lacks `internal_locus`; editing it would cascade ~22 pins) — the queue already
  has both the shadow flag and the coverage decisions, so the exception lives there.

## Standing constraints
Research/advisory only; no production authority/submission/severity/reportable/confirmed; no production/contest source
edits; active audit `size-credit-2024-06-blind` symlink unchanged; no target/award hard-coding; forbidden 5 + do-not-edit
(router incl.) byte-identical.
