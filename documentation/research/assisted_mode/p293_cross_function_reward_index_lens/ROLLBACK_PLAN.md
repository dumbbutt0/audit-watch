# P293 — ROLLBACK_PLAN

To fully revert P293 (restore the P292 state):

1. `scripts/research/invariant_delta_deriver.py` → restore to sha256[:16] `cf7de22e7bb29fd7`
   (remove `_lens_reward_index_cross` + `_l3_*` helpers + config-family reads/regexes; restore the
   `_lens_reward_index_init(item, body)` lambda in `derive()`; remove the held-lens3 surfacing on the no-deviation
   branch).
2. `config/research_invariant_delta_deriver.json` → restore to `39d3cf44736d78e8` (remove the `lens3_*` keys).
3. `scripts/research/completion_evidence_deriver.py` → restore to `bd4994f6aa2a9638` (remove the scoped
   fill-if-missing of root_cause/runner_up_mechanism).
4. Revert the DO_NOT_EDIT hash-pin bumps in `tests/research/test_p285,p286,p291,p292` back to the P292 hashes.
5. Delete `tests/research/test_p293_cross_function_reward_index_lens.py` and this docs dir.

Effect of rollback: `_increaseUserShare` returns to `NEEDS_VALUE_FLOW_EVIDENCE` (the P292-B residual); the tracer,
gate, router, reused detectors, and forbidden 5 are already byte-identical so need no restore.
