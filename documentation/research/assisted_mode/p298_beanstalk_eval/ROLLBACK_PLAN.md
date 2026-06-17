# P298 — ROLLBACK_PLAN

P298 adds only new files; no existing module/config/answer-key/contest-source was edited.
1. Delete `scripts/research/beanstalk_eval_{score,novelty,validity}.py` + `config/research_beanstalk_eval.json`.
2. Delete `pocs/p298/` (the 5 Tier-C PoCs).
3. Delete `tests/research/test_p298_beanstalk_eval.py` + this docs dir.
The P294 verifier, reused PoC scripts, forbidden 5, the answer key (match_matrix + ground_truth), and the contest
source are byte-identical / untouched. No hash pins bumped. The kb-search + immunefi MCP config was already present
(only verified, not changed).
