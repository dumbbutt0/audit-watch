# P286 — ROLLBACK_PLAN

P286 is purely additive (a new PoC project + docs + one research test); it changes no pipeline module.

## 1. Disable (no removal)
Nothing imports `pocs/p286/`. Not running `forge test` there = no effect.

## 2. Full removal
Delete `pocs/p286/`, `tests/research/test_p286_ready_set_poc_sweep.py`, and this docs dir. No frozen module, the reused
detector platform, the forbidden 5, or `pocs/p281` is touched by P286, so removal restores the P285 state exactly.

## Note
P286 made NO source changes to the extractor/gate/deriver/tracer — it only exercises the P285 READY outputs with a PoC.
There is nothing in the pipeline to revert.

## Verification after removal
`pytest tests/research/test_p285_inline_guard_granularity.py` green · `cd pocs/p281 && forge test` (2 passed) ·
`output` symlink → `audits/size-credit-2024-06-blind/output`.
