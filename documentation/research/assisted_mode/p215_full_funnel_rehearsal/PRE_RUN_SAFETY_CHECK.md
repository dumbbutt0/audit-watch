# P215 — PRE-RUN SAFETY CHECK

**Phase:** P215 — Finished-contest full-funnel rehearsal with L3 readiness enabled
**Date:** 2026-06-06
**Mode:** human-review rehearsal on a **completed** contest. NOT a live bounty submission.

## Safety preconditions (all must hold before any run step)

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Target is a **finished** contest | ✅ | ZetaChain Code4rena `2023-10-zetachain` (contest closed Oct 2023). |
| 2 | Answer key **exists and is sealed** | ✅ | `audits/zetachain-2023-10-holdout/_sealed_answer_key/` (own `.git`, `report.md` 401033 B, `README.md`, `data/`). Only the README title line was glanced to confirm it is the marker; **finding bodies NOT read.** |
| 3 | No live bounty route is in scope | ✅ | Contest is closed; no submission target exists. |
| 4 | No external submission endpoint will be used | ✅ | Repo has **no external submission code** — all `submit`/`platform` code is local draft-only (`final_submission_pack.py`, `submission/renderers/platform_renderer.py` emit "DRAFT ONLY — NOT SUBMITTED"; `submission/gates/submission_gate.py` forces `human_approval_required=true`). Verified by grep across `*.py`/`*.sh`. |
| 5 | Dry-run queue path is **local only** | ✅ | `output_research/dry_run_submission_queue/` — local JSONL + per-candidate records, `research_only:true`, `routes_in_production:false`. Submits nowhere. |
| 6 | L3 flag enabled **in-process only** | ✅ | `AUDITWATCH_L3_READINESS=1` exported only in the rehearsal shell; **unset at END**; never written to any config file. |
| 7 | `runtime_policy.api_free=true` | ✅ | `config/runtime_policy.json` = `{"api_free": true, ...}` (hash `bea43487`). **File will not be modified.** |
| 8 | Active live audit not disturbed | ✅ (plan) | Active = `quantamm-2024-12-eval`. Switch-then-**restore**: record active → switch to holdout → run → switch back to quantamm → verify `config/active_audit.json` restored. quantamm workspace files never touched. |
| 9 | Human review mandatory before any real submission | ✅ | No "ready" state flips `submission_ready`/`routing_allowed`; dry-run queue records carry `human_review_required:true`. |

## Required safety mode — enforced, not configured
The spec's flags `route_to_platform=false` / `external_submission=false` / `dry_run_submission_queue=true` /
`human_review_required=true` are **not config keys** in this repo (only `api_free` lives in `runtime_policy.json`).
They are **enforced by absence + invariant**:
- No external routing/submission code path exists anywhere (check #4) ⇒ `route_to_platform`/`external_submission` are
  structurally false.
- `api_free=true` blocks any live LLM/API egress.
- `submission_gate.py` hard-codes `human_approval_required=true`.
- `submission_readiness_review.record_review()` is append-only and never flips canonical flags.

**Do NOT add live-routing keys to `runtime_policy.json`.** Modifying that file to enable routing is an ABORT condition.

## Abort conditions (→ `HUNT_ABORTED_TOOLING_RISK` / `HUNT_ABORTED_SCOPE_RISK`)
Abort immediately and record the abort decision if any of these occur:
1. Any external submission path activates (HTTP POST to a platform, clipboard/browser automation).
2. `runtime_policy.json` is modified to enable live routing.
3. The answer key is opened **before** `FREEZE_MANIFEST.md` hash is recorded.
4. The active quantamm audit is disturbed and not restored.
5. The dashboard exposes submit/promote controls.
6. Canonical submission flags (`submission_ready`/`routing_allowed`) are flipped without explicit human action.
7. A High enters the dry-run queue without L3 PASS or a written human override.
8. A High report package omits PoC / L3 evidence.

## Production-code freeze (must be byte-identical START==END)
`prompts/deep_trace.md`, `scripts/min_confirm_gate.py`, `scripts/confirm_gate.py`,
`scripts/submission_readiness_review.py`, `scripts/validate_p208_l3_readiness.py`,
`scripts/dashboard.py`, `scripts/final_submission_pack.py`, `scripts/audit_manager.py`,
`scripts/audit_context.py`, `scripts/triage_write.py`, `config/runtime_policy.json`,
`config/agent_policy.json`, `data/fp_autopsies/rejection_rules.jsonl`,
`output_research/option_a_campaign/ledger.jsonl`. (START hashes in `INTEGRITY_PRECHECK.md`.)

**Conclusion: all safety preconditions hold. Cleared to begin the rehearsal.**
