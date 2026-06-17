# P289 — ROLLBACK_PLAN

P289 is additive within the research deriver; un-wired; default-off.

## 1. Disable
Not running the deriver/gate = no effect. The lenses only fire inside `invariant_delta_deriver.derive()` (research).

## 2. Revert the lenses, keep everything else
Remove the 4 lens functions + their entries in `derive()`'s `found` loop and the 4 new statuses + signal lists from
`config/research_invariant_delta_deriver.json`; restore the prior deriver/config hashes
(`dd549b9f…`/`3eb86fcc…`) in the test_p285/p286 FROZEN pins and the test_p287/p288 exclusion. Behavior reverts to P288
exactly (ECG → 0 READY).

## 3. Full removal
Also delete `tests/research/test_p289_loss_reward_lenses.py` and this docs dir. No frozen-others module, reused detector,
forbidden file, active audit, or contest source is touched by P289, so removal restores the P288 state.

## Verification after rollback
`pytest tests/research/test_p288_second_fresh_blind_generalization.py` green · frozen-others + forbidden 5 sha256
unchanged · `output` symlink → `audits/size-credit-2024-06-blind/output`.
