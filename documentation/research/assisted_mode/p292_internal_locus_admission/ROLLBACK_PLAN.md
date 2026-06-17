# P292 — ROLLBACK_PLAN

P292 edits only `expanded_validation_queue.py` + its config.

## 1. Disable
Set `internal_locus_admission.enabled=false` in the queue config → no admission exception; the queue reverts to
handoff-only (P291 behavior). No code change needed.

## 2. Full revert
Remove the internal-locus admission block in `expanded_validation_queue.build` + the `internal_locus_admission` config
block; restore the queue/config hash pins (374e1689/8dc7556e) and remove the queue+config from the P287/p288/p290
exclusions; delete `tests/research/test_p292_*.py` + this docs dir. No router, frozen-others, forbidden file, active
audit, or contest source is touched → removal restores P291 exactly.

## Verification after rollback
`pytest tests/research/test_p291_*.py` green · router + do-not-edit modules + forbidden 5 sha256 unchanged · `output`
symlink → `audits/size-credit-2024-06-blind/output`.
