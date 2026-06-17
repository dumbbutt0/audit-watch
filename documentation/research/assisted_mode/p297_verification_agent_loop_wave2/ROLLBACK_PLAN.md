# P297 — ROLLBACK_PLAN

1. Revert the additive `--out-dir` / `judge(out, specs_path)` change in
   `scripts/research/verification_agent_loop.py` (it is additive; default behavior unchanged — reverting is optional).
2. Delete the 6 wave-2 PoC dirs: `pocs/p296/{ecg-2023-12-holdout__H-01,ecg-2023-12-holdout__M-02,
   ecg-2023-12-holdout__M-03,kelp-2023-11-holdout__M-01,kelp-2023-11-holdout__M-02,salty-2024-01-holdout__H-05}/`.
3. Delete `tests/research/test_p297_verification_agent_loop_wave2.py` + this docs dir.

The P294 verifier, reused PoC scripts, forbidden 5, the P296 wave-1 PoCs + snapshot, and answer keys are
byte-identical / untouched. No hash pins were bumped.
