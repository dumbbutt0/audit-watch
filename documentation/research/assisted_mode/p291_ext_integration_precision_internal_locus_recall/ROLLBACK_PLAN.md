# P291 — ROLLBACK_PLAN

P291 edits 4 research modules/configs (deriver, gate, deriver-config; harness, harness-config) + downstream pin bumps.

## 1. Disable
Part A: EXTERNAL_INTEGRATION block only fires inside the research gate; not running it = no effect. Part B internal-locus
expansion is gated by `internal_locus_recall.enabled` in the harness config — set false to disable surfacing.

## 2. Revert Part B only (keep Part A)
Remove `_expand_internal_loci` + its call in `recall_first_harness.run()` + the imports; remove the `internal_locus_recall`
config block; restore the harness/harness-config hash pins (85f9cbe / e9b74687) in the pinning tests and the P287/p288/
p290 exclusions. Part A (EXTERNAL_INTEGRATION precision) stays.

## 3. Revert Part A only (keep Part B)
Remove the `_integration_deviation_evidence` helper + attach in the deriver, the gate block + `_integration_deviation` +
status + the deriver-config terms; restore deriver/gate hash pins. Part B stays.

## 4. Full removal
Revert all 4 files to the P290 state (deriver bd4994f6→c41eaf9d, gate 7afdc560→9a4e3834, harness be428a12→85f9cbe,
configs), delete `tests/research/test_p291_*.py` + this docs dir, restore all bumped pins + remove the P291 exclusions.
No frozen-others (router/tracer/P289 lenses/reused platform), forbidden 5, active audit, or contest source is touched →
removal restores P290 exactly.

## Verification after any rollback
`pytest tests/research/test_p290*.py` green · forbidden 5 + do-not-edit modules sha256 unchanged · `output` symlink →
`audits/size-credit-2024-06-blind/output`.
