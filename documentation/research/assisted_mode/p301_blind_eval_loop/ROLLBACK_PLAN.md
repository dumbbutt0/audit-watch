# P301 — ROLLBACK_PLAN

P301 adds only new files (no existing module/config/answer-key/ground_truth edited; verifier reused unchanged).
1. Delete `scripts/research/blind_eval_loop.py` + `config/research_blind_eval_suite.json`.
2. Delete `pocs/p301/`, `tests/research/test_p301_blind_eval_loop.py`, this docs dir (incl. outputs/loop_state.json).
3. Delete `data/learning/_proposed/recall_gap_backlog.jsonl` (a staged backlog; never promoted).
The P294 verifier (1a005811), forbidden 5, ground_truth, rejection_rules.jsonl, answer-key match_matrices, and contest
source are byte-identical / untouched. No hash pins bumped. No ScheduleWakeup loop was started.
