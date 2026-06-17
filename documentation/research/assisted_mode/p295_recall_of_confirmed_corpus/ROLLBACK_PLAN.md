# P295 — ROLLBACK_PLAN

P295 adds only new files + 3 poc_manifest.json + a minor faithful L1/L2 strengthening of two existing PoC tests.

1. Delete `scripts/research/recall_of_confirmed_corpus.py` + `config/research_recall_corpus_map.json`.
2. Delete `tests/research/test_p295_recall_of_confirmed_corpus.py` + this docs dir.
3. Delete `pocs/p295/` and the manifests `pocs/p287/kelp/.../poc_manifest.json`, `pocs/p281/poc_manifest.json`.
4. Revert the L1/L2 edits in `pocs/p287/.../P287_KelpOracleStaleness.t.sol` and
   `pocs/p281/test/P281_GovernorStateMachine.t.sol` (named before/after + attacker prank) — both still PASS either way;
   reverting only changes whether the verifier scores them L1/L2-complete.

No existing module/config was edited; the P294 verifier, reused PoC scripts, 4 taxonomies, tracer, gate, and forbidden
5 are byte-identical; answer keys were never written.
