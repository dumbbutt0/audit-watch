# P294 — ROLLBACK_PLAN

P294 adds ONLY new files — rollback is deletion, with zero impact on any existing module (nothing was edited).

1. Delete `scripts/research/executed_poc_verifier.py` + `config/research_executed_poc_verifier.json`.
2. Delete `tests/research/test_p294_executed_poc_verifier.py` + this docs dir (incl. `proof_driver.py`).
3. Delete `pocs/p294/` and the three `poc_manifest.json` files (pocs/p286, pocs/p290/.../Pools_deposit, pocs/p294/...).
4. Optionally remove `output/poc_validation/raw/p294_*.log`.

No hash pins were bumped (no existing module changed); the 4 taxonomies, tracer, gate, reused PoC scripts, and
forbidden 5 are untouched. `ground_truth.jsonl` was never written.
