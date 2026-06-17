# P287 — ROLLBACK_PLAN

P287 is a measurement phase: it ran the FROZEN stack read-only and added only new artifacts (docs, outputs, one PoC
project, one research test). It edited NO pipeline module.

## 1. Disable / no-op
Nothing imports the P287 artifacts. The frozen stack was run as-is; there is no behavior change to revert.

## 2. Full removal
Delete `documentation/research/assisted_mode/p287_fresh_blind_generalization/`, `pocs/p287/`, and
`tests/research/test_p287_fresh_blind_generalization.py`. No frozen module, reused detector, forbidden file, active audit,
or contest source is touched by P287, so removal restores the P286 state exactly.

## Verification after removal
`pytest tests/research/test_p286_ready_set_poc_sweep.py` green · frozen stack + forbidden 5 sha256 unchanged ·
`output` symlink → `audits/size-credit-2024-06-blind/output`.
