# P290 — ROLLBACK_PLAN

P290 is a measurement phase: it ran the FROZEN stack read-only and added only new artifacts (docs, outputs, one Tier-C
PoC, one research test). It edited NO pipeline module.

## 1. No-op
Nothing imports the P290 artifacts; the frozen stack was run as-is. There is no behavior change to revert.

## 2. Full removal
Delete `documentation/research/assisted_mode/p290_fresh_blind_loss_reward_lens_retest/`,
`pocs/p290/salty-2024-01-holdout/`, and `tests/research/test_p290_fresh_blind_loss_reward_lens_retest.py`. No frozen
module, reused detector, forbidden file, active audit, or contest source is touched by P290, so removal restores the
P289 state exactly.

## Verification after removal
`pytest tests/research/test_p289_loss_reward_lenses.py` green · frozen stack + forbidden 5 sha256 unchanged · `output`
symlink → `audits/size-credit-2024-06-blind/output`.
