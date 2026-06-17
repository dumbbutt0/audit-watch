# P300 — ROLLBACK_PLAN

P300 adds only new files (no existing module/config/answer-key/ground_truth edited; verifier reused unchanged).
1. Delete `scripts/research/eval_campaign.py` + `scripts/research/submission_filter.py` + `config/research_eval_campaign.json`.
2. Delete `pocs/p300/`, `tests/research/test_p300_calibration_campaign.py`, this docs dir.
3. Delete `data/learning/_proposed/p300_rejection_rule_proposals.jsonl` (a staged proposal; never promoted).
The P294 verifier (1a005811), forbidden 5, answer-key match_matrices, ground_truth, and rejection_rules.jsonl are
byte-identical / untouched. No hash pins bumped.
