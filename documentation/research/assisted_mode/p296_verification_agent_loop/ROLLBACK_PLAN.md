# P296 — ROLLBACK_PLAN

P296 adds only new files (loop harness + config + pocs/p296/* + tests + docs); no existing module was edited.

1. Delete `scripts/research/verification_agent_loop.py` + `config/research_verification_agent_loop.json`.
2. Delete `pocs/p296/` (all subagent PoC dirs).
3. Delete `tests/research/test_p296_verification_agent_loop.py` + this docs dir.
4. Optionally remove `output/poc_validation/raw/p294_*` logs created by the judge runs.

The P294 verifier, reused PoC scripts, forbidden 5, the 4 taxonomies, tracer, gate, and answer keys are byte-identical
/ untouched. No hash pins were bumped.
