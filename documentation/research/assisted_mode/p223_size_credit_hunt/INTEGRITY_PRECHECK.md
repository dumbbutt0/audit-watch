# P223 — Integrity precheck (START)

Date: 2026-06-07 · `api_free=true` · research-only · 0 route/submit/promote intended.

## Pre-existing active audit (RESTORE at END)
`zetachain-2023-10-holdout` (switched_at 2026-06-07T04:59:00Z). Must be the active audit again at END.

## L3 flag
`AUDITWATCH_L3_READINESS` will be set **in-process only** (default-off globally); unset at END.

## Production + helper file START hashes (md5 first-8)
| file | START |
|------|-------|
| prompts/deep_trace.md | ef93a6c2 |
| scripts/min_confirm_gate.py | 41dd3c96 |
| scripts/confirm_gate.py | 4fadfc5f |
| scripts/submission_readiness_review.py | e4960878 |
| scripts/validate_p208_l3_readiness.py | fe37e6ad |
| scripts/dashboard.py | 9de16b68 |
| scripts/dashboard_sync.py | 26bd7ee0 |
| scripts/final_submission_pack.py | 57cba16d |
| scripts/sync_hunt_findings.py | a060a992 |
| scripts/validate_hunt_sync_completion.py | 10c492f5 |
| scripts/human_review_priority.py | cbdfc7fd |
| scripts/finding_detail.py | 0f57665e |
| scripts/funnel.py | 89ac489a |
| scripts/findings_overview.py | 01159526 |
| config/runtime_policy.json | bea43487 |

All match the P222 END state → production is clean entering P223. **Forbidden (no edits):**
`prompts/deep_trace.md`, `scripts/min_confirm_gate.py`, `scripts/confirm_gate.py`,
`scripts/dashboard_sync.py`, and `decide()` in `scripts/validate_p208_l3_readiness.py`.

## Blindness witness — sealed answer key (contents NOT read)
`sha256 = 8eacd8059e1dfbe12b297e044c3a36279edbd5ad7fe98d8319139d856c0a9c23`
(identical for both copies):
- `audits/size-credit-2024-06/output/eval_ready/size_fresh/answer_key.md`
- `audits/size-credit-2024-06/output/pre_answer_key_snapshot/documentation__evals__size-credit-2024-06__answer_key.md`

This hash will be re-checked at Step 9 (scoring) to prove the key was unchanged and unread until then.

### Sealed paths — MUST NOT be read during discovery (Steps 2–8)
- `audits/size-credit-2024-06/output/eval_ready/size_fresh/answer_key.md`
- `audits/size-credit-2024-06/output/eval_ready/size_fresh/candidate_H-03.json`
- `audits/size-credit-2024-06/output/eval_ready/size_fresh/route_scorecard.json`
- `audits/size-credit-2024-06/output/pre_answer_key_snapshot/documentation__evals__size-credit-2024-06__answer_key.md`
- `audits/size-credit-2024-06/output/pre_answer_key_snapshot/documentation__evals__size-credit-2024-06__candidate_H-03.md`

## Original Size Credit workspace (MUST be untouched START==END)
`audits/size-credit-2024-06/output` — combined md5 fingerprint `62901f774f9e`, 65 files.
The blind hunt forks a new workspace `size-credit-2024-06-blind`; the original workspace is read only for the
sealed key at scoring time and is otherwise never written.
