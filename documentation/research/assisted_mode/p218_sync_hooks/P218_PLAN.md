# P218 — Mandatory dashboard-sync hooks + completion guard for the Zeta funnel

## Context
P216 created the synced-finding dashboard contract; P217 added the generic per-hunt wrapper
(`scripts/sync_hunt_findings.py`) that populates fields from real artifacts (Zeta completeness 57%→90%). But the
wrapper is still **optional** — a future run can forget to call it. P218 makes syncing **enforced**: a completion
guard that fails unless every required dashboard/readiness artifact is current + a thin mandatory hook that runs the
wrapper then the guard. Exercised on Zeta via **REPLAY_MODE** (reuse the frozen P215 artifacts; the new hook+guard are
the deliverable, not re-discovery). Integration is a **standalone documented command** — `run_pipeline.sh` is shared
across all audits and is NOT edited (avoids firing the research sync for unrelated production audits).

Confirmed state: mirror has 12 ZETA records; dry-run-queue = ZETA-04/07/12; L3 records exist for 9 of 12 (not
02/09/12); `sync_hunt_findings.main(argv)` is importable; `dashboard_sync.validate_synced`/`safety_ok` enforce safety.

## Decisions (user-confirmed)
- **Re-run = REPLAY_MODE** (frozen P215 artifacts → mandatory hook → completion validator; document what was not re-run).
- **Integration = standalone hook + completion guard** (no `run_pipeline.sh` edit).

## Approach
1. **Completion guard** `scripts/validate_hunt_sync_completion.py` — args `--phase --audit --workspace
   --candidate-register --synced-mirror --l3-dir --dry-run-queue --strict` (+ `--metrics`). Structured as a **pure**
   `run_checks(candidates, synced_by_id, l3_dir, drq_ids, opts) -> (failures, warnings, report)` (fast, hermetic, used
   by tests) **plus** live reader/card checks (`check_readers`, `check_cards`, injectable loaders). Checks:
   1. every register candidate has a synced record (by candidate_id) — FAIL if missing.
   2. no extra stale phase/audit synced records absent from the register (unless `--allow-extra`) — FAIL.
   3. every synced record `dashboard_sync.validate_synced(rec)==[]` — FAIL.
   4. every record `safety_ok` (9 safety flags + canonical_submission_ready_source) — FAIL.
   5. readers see each record: `funnel.load_records()` + `findings_overview.load_overview()` — FAIL.
   6. detail card loads for each (`finding_detail.load_unified_detail("funnel:<id>")` → 15 verifier sections, no
      exception) — FAIL.
   7. High/Critical blocked unless L3 PASS/HUMAN_OVERRIDE: a High/Critical record with `high_promotion_allowed is True`
      and `l3_status ∉ {PASS,HUMAN_OVERRIDE}` — FAIL.
   8. every dry-run-queue id has a synced record — FAIL.
   9. queued candidate references its package/queue (`source_refs.dry_run_queue`) — WARN (FAIL under `--strict`).
   10. sync metrics file present with sync counts — WARN/info.
   Exit non-zero on any failure (or warning under `--strict`); emit a JSON report.
2. **Mandatory hook** `scripts/run_hunt_sync_hook.py` — args mirror the wrapper. Runs
   `sync_hunt_findings.main([... ,"--write","--strict"])` then `validate_hunt_sync_completion.main([... ,"--strict"])`;
   writes sync metrics to `output_research/funnel/sync_hook_metrics.json` (configurable); logs exactly what was synced;
   idempotent (wrapper backs up + byte-identical re-run); **exits non-zero if either step fails**. Writes only the
   generated mirror + sync metrics; no route/submit.
3. **Required write contract** (`REQUIRED_WRITE_CONTRACT.md`) — per-candidate required targets + the explicit-missing
   tokens (`unknown`/`MISSING_EVIDENCE`/`NOT_ATTEMPTED`/`NEEDS_HARNESS`/`BLOCKED`); silent omission forbidden.
4. **REPLAY_MODE exercise** — run `run_hunt_sync_hook.py --phase P215 --audit zetachain-2023-10-holdout --workspace …`
   → regenerates the mirror (expected byte-identical to P217), validator passes, sync metrics written. Document that
   discovery/deep_trace/triage/L3-harness were reused frozen (not re-run).
5. **Hook-failure tests** `tests/research/test_hunt_sync_completion.py` — call the pure `run_checks` (+ injectable
   card/reader loaders) with crafted inputs to prove FAIL on: missing candidate · unsafe flags · High without
   L3 PASS/blocker · dry-run-queue entry without synced record · duplicate record_ids · malformed/invalid record ·
   missing package link for a queued candidate (strict) · detail card cannot load. Plus a happy-path pass.

## Files
- **New:** `scripts/validate_hunt_sync_completion.py`, `scripts/run_hunt_sync_hook.py`,
  `tests/research/test_hunt_sync_completion.py`, `documentation/research/assisted_mode/p218_sync_hooks/` (14 docs +
  `metrics.json` + `integrity_checks.md`), `output_research/funnel/sync_hook_metrics.json` (sync metrics).
- **Regenerated (data, expected byte-identical):** `documentation/research/funnel/synced_findings.generated.json`.
- **Unchanged (verify byte-identical):** `scripts/sync_hunt_findings.py`, `scripts/dashboard_sync.py`,
  `scripts/build_synced_findings.py`, `scripts/funnel.py`, `scripts/finding_detail.py`, `scripts/findings_overview.py`,
  `scripts/dashboard.py`, `scripts/submission_readiness_review.py`, `scripts/final_submission_pack.py`,
  `run_pipeline.sh`, `documentation/research/funnel/funnel_records.json`, `config/runtime_policy.json`,
  `output_research/option_a_campaign/ledger.jsonl`, and forbidden `deep_trace.md`/`min_confirm_gate.py`/`confirm_gate.py`.

## Verification
1. Integrity START/END md5 of the files above; only new files + (possibly) the mirror + sync metrics change.
   `api_free=true`; active audit recorded.
2. `run_hunt_sync_hook.py` (P215 args): wrapper writes 12, validator exits 0, sync metrics written; re-run
   byte-identical (idempotent); mirror unchanged vs P217.
3. Validator catches all 8 failure modes (tests) and passes the real P215 set.
4. Dashboard: 12 ZETA in `/findings`,`/candidates`,`/funnel`; cards 15/15; L3 + blockers + queue + PoC links render;
   unknowns explicit; no submit/promote controls; no active-audit switch.
5. Completeness reconfirmed (90%, artifact-backed) via the wrapper scorer.
6. Tests: new `test_hunt_sync_completion.py` + P217 sync + dashboard_sync + funnel/overview/detail + submission
   readiness → all pass; 0 route/submit side effects.

## Deliverables
P218_PLAN.md · INTEGRITY_PRECHECK.md · CURRENT_ZETA_PIPELINE_MAP.md · REQUIRED_WRITE_CONTRACT.md ·
HOOK_IMPLEMENTATION.md · ZETA_RERUN_OR_REPLAY_RESULTS.md · SYNC_COMPLETION_VALIDATION.md ·
DASHBOARD_POPULATION_RESULTS.md · FIELD_COMPLETENESS_SCORECARD.md · HOOK_FAILURE_TESTS.md · TEST_RESULTS.md ·
P218_RECOMMENDATION.md · metrics.json · integrity_checks.md.

## Decision space
`SYNC_HOOKS_READY` (hook + completion guard exist and are enforced; Zeta re-synced through the hook via documented
REPLAY_MODE; all 12 in all three pages; cards 15/15; completeness confirmed/improved; missing fields explicit; unsafe /
missing / duplicate / no-L3-High / queue-without-sync records all FAIL the guard; no submit/route/promote; idempotent +
reversible; hashes recorded; JSON valid) · `SYNC_HOOKS_PARTIAL_REPLAY_ONLY` (fallback if any gap or if replay deemed
insufficient) · `SYNC_HOOKS_FAILED_COMPLETION_GUARD` · `SYNC_HOOKS_FAILED_VISIBILITY` · `SYNC_HOOKS_FAILED_SAFETY` ·
`INVALID_RUN`. **Expected: SYNC_HOOKS_READY (REPLAY_MODE-exercised).**
