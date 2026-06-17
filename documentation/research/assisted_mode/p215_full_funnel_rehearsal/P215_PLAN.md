# P215 — Finished-contest full-funnel rehearsal with L3 readiness enabled

## Context
P211 rehearsed only the L3 *wired surface* (readiness→dashboard→package); P212 generated real candidates but routed
them through a **side page**, not the real funnel. P215 closes that gap: take real candidates from a finished contest
and push them through the **actual pipeline funnel** — a real audit workspace, coverage manifest, candidate register,
triage, confirm gates, L3 readiness (flag on), report packaging, a **local dry-run submission queue**, and dashboard
review — then score against the sealed answer key *after a freeze*. This is a rehearsal on a completed contest: **no
external submission, no route-to-platform, no auto-submit, human review mandatory.** The goal is to prove the funnel
routes the right candidates and that L3 blocks inflated Highs without under-rating real ones, on a target never used in
the L3 loop.

## Decisions (confirmed with user)
- **Target:** `audits/zetachain-2023-10-holdout` (C4; 37 contracts / ~3411 LOC; 14 High + 34 Medium; sealed
  `_sealed_answer_key/` with own `.git` + 401KB `report.md`; **not** in the L3 avoid-list). Already has
  `output/coverage_manifest.json` + `output/deep_pass/_bundles/` (dp_0000–0006) + `candidate_queue.json` staged blind.
- **Active audit:** **switch-then-restore.** Record current active (`quantamm-2024-12-eval`), `switch` to the holdout for
  the run, **switch back to quantamm at the end and verify restoration.** quantamm workspace files are never touched.
- **Discovery:** **bounded blind deep_trace.** Reuse the pre-staged deep_pass bundles + key-blind deep_trace Sonnet
  subagents to produce **≤12 candidates / ≤5 deep traces / ≤3 harnesses**; emphasis on *routing through real gates*,
  not exhaustive recall.

## Required safety mode (enforced, not configured)
- `AUDITWATCH_L3_READINESS=1` **in-process only** (export in the rehearsal shell; unset at END).
- `runtime_policy.api_free=true` (already true — **do not modify the file**).
- `route_to_platform=false` / `external_submission=false` / `dry_run_submission_queue=true` /
  `human_review_required=true`: these keys **do not exist** in config and **no external submission code path exists**
  anywhere (verified: all `submit`/`platform` code is local draft-only). They are **enforced by absence** + `api_free`
  + the `submission_gate.py` invariant `human_approval_required=true`. **Do NOT add live-routing keys to
  runtime_policy.json** (modifying it to enable routing is an abort condition). Document this in PRE_RUN_SAFETY_CHECK.

## Hard scope / non-negotiables
- Do not modify `deep_trace.md`, `min_confirm_gate.py`, `confirm_gate.py`, or the L3 gate
  (`validate_p208_l3_readiness.py`, `submission_readiness_review.py`) during the run.
- No external submit / route / auto-submit / promote / demote. Any "route"/"submission" output is **local dry-run only.**
- Do not open `_sealed_answer_key/report.md` (or its `data/`) before the freeze.
- Do not rewrite historical/frozen artifacts (P204/P207/P212 records, ledgers). The holdout's own `output/`/`data/` are
  the audit's working substrate — **snapshot START, add to them, preserve the pre-staged blind bundles** (don't clobber).
- Human review remains mandatory.

## Sequence (maps the spec's 17 steps onto the real funnel)
1. **PRE_RUN_SAFETY_CHECK.md** — confirm: finished contest; answer key exists + sealed; no live route in scope; dry-run
   queue is local only; L3 flag in-process only; `api_free=true`; active quantamm audit will be restored; human review
   mandatory. Define the abort conditions (step 14).
2. **INTEGRITY_PRECHECK.md** — record START md5(first-8): `deep_trace.md`, `min_confirm_gate.py`, `confirm_gate.py`,
   `submission_readiness_review.py`, `dashboard.py`, `validate_p208_l3_readiness.py`, `L3_READINESS_SCHEMA.json`,
   `final_submission_pack.py`, `audit_manager.py`, `audit_context.py`, `runtime_policy.json`,
   `data/fp_autopsies/rejection_rules.jsonl` (+ campaign ledger), the holdout **source tree** hash, the
   `_sealed_answer_key/` seal marker, and `config/active_audit.json` (= quantamm). All production files must be
   byte-identical START==END.
3. **TARGET_SELECTION.md** + **TARGET_INTAKE.md** — zetachain rationale; from `meta.json`/`foundry.toml`: commit,
   answer-key path + seal status, in-scope vs out-of-scope contracts, build/test commands, solc/deps, contest severity
   rules, why suitable.
4. **Activate workspace** — capture `config/active_audit.json` (quantamm), then
   `python scripts/audit_manager.py switch zetachain-2023-10-holdout`. The `output/` symlink follows. Confirm the real
   funnel directories exist (`output/`, `data/triage/`, `data/findings/`, `pocs/`, reports). Snapshot START state of
   `output/` (so additions are auditable).
5. **COVERAGE_MANIFEST.md** — reuse/refresh `output/coverage_manifest.json` via
   `./run_pipeline.sh coverage-manifest` (source-only); summarize entry points, deposits/withdrawals/claims, accounting
   transitions, custody, access-control, oracle/price, signature validation, callbacks/hooks, upgrade/admin, invariant
   families.
6. **Candidate discovery (capped ≤12)** — key-blind deep_trace Sonnet subagents over the pre-staged deep_pass bundles
   (JSON-only, token-scan clean, **no answer-key access**). Every candidate gets an id (`ZETA-01…`), source refs, and an
   impact_class/threat_ceiling. Source-refuted candidates are rejected early **but recorded**. Write into the **real
   substrate**: `output/findings_deep_trace.json` (specialist shape) → `output/merged_findings.json` via the report
   generator. **CANDIDATE_REGISTER.json** = frozen snapshot.
7. **Route through the real funnel** — for each candidate run the genuine stages and capture every output + blocker:
   - **Triage:** `/triage` → `python scripts/triage_write.py` → `data/triage/{submit,poc_required,downgraded,
     merged,rejected,human_review_queue}.jsonl` + `<ID>.md`. → **TRIAGE_RESULTS.md**, **DEEP_TRACE_RESULTS.md**.
   - **min_confirm_gate** (`scripts/min_confirm_gate.py` → `output/min_confirm_gate.json`).
   - **confirm_gate** both modes: `--mode eval` (advisory, exit 0) and `--mode submission` (hard-fail High/Critical
     non-credible). → **CONFIRM_GATE_RESULTS.md**.
   - **submission_readiness_review** with flag on (`l3_evaluate` + `evaluate`) → **SUBMISSION_READINESS_RESULTS.md**;
     separate **threat ceiling** from **calibrated severity**. Never flips `submission_ready`/`routing_allowed`.
8. **L3 readiness + harness (≤3)** — author per-candidate L3 records at
   `output_research/l3_readiness/ZETA-*.json` (schema = `L3_READINESS_SCHEMA.json`). With the flag on: High/Critical
   need **L3 PASS or written human override**; deterministic core-path DoS High needs the 10 carve-out fields + notes;
   missing/malformed L3 on a High **fails closed**; Medium needs source-proven impact; source-refuted can't route.
   Build Foundry harnesses (forge-std-free pattern; real source via `realsrc/` copy; **only external deps mocked**;
   honest control case) **only** for High-ceiling candidates with statically-unclear realized impact. → **HARNESS_RESULTS.md**.
9. **Dry-run submission queue (local)** — `output_research/dry_run_submission_queue/` (JSONL ledger + per-candidate
   records). A candidate enters **only** if: report package exists; readiness = human-reviewable; High has L3 PASS or
   written override; Medium has source-proven impact; `human_review_required=true`; `external_submission=false`. Each
   record: candidate id, severity recommendation, readiness state, blocker state, package path, L3 status, PoC
   path/command, human-review checklist, and `research_only:true`/`routes_in_production:false`. **It submits nowhere.**
10. **Report packages** — `python scripts/final_submission_pack.py` → `output/submission_pack.{md,json}`; copy
    per-candidate packages into deliverable `REPORT_PACKAGES/`. High packages must carry PoC + L3 evidence.
11. **DASHBOARD_REVIEW.md** — with flag on, verify (via `/api/state`, `/findings`, `/api/submission-readiness`, and the
    L3 panel) that the dashboard shows candidates, stage status, readiness blockers, L3 status, package links, dry-run
    queue state, **no submit/promote controls**, and sealed-key status. (Dashboard server launch is flaky in-harness —
    verify by calling the route functions directly if needed; leave 0 stray processes.)
12. **FREEZE_MANIFEST.md** — freeze + hash: candidate register, triage outputs, deep_trace results, confirm-gate
    results, L3 records, harness results, report packages, dry-run queue, dashboard/API snapshot, metrics. **No scoring
    before this freeze.**
13. **Controlled scoring (post-freeze)** — open `_sealed_answer_key/report.md`; score each candidate
    HIT/PARTIAL/ADJACENT/MISS/TRUE_NEGATIVE/FALSE_POSITIVE/FALSE_NEGATIVE/WRONG_MECHANISM and
    SEVERITY_MATCH/UNDER/OVER. Separately score discovery recall, candidate precision, confirm-gate precision, L3
    severity calibration, package completeness, dry-run-queue correctness.
14. **Stop conditions** — abort with `HUNT_ABORTED_TOOLING_RISK`/`HUNT_ABORTED_SCOPE_RISK` if: any external submission
    path activates; `runtime_policy.json` modified to enable live routing; answer key opened before freeze; quantamm
    disturbed (not restored); dashboard exposes submit/promote; canonical submission flags flipped without human action;
    a High enters the dry-run queue without L3 PASS/written override; a High package omits PoC/L3 evidence.
15. **metrics.json** — all fields from the spec (target, candidates_generated/deep_traced/confirmed/rejected,
    source_refuted_count, high_ceiling_count, l3_harness_attempts, l3_pass_count, high_blocked_missing_l3,
    medium/high_human_reviewable, dry_run_queue_count, false_queue_entries_after_scoring, hits/partials/adjacent/misses,
    false_positives, severity_over/under, route_submit_side_effects, dashboard_mismatches, package_completeness_score).
16. **Restore + integrity END** — `switch` back to `quantamm-2024-12-eval`; unset `AUDITWATCH_L3_READINESS`; recompute
    END hashes (production byte-identical START==END); kill stray dashboard procs; write **integrity_checks.md**.
17. **Post-score analysis + decision** — write the analysis deliverables and end with one decision.

## Files / artifacts
- **Reads/uses (no edits):** `run_pipeline.sh`, `scripts/{audit_manager,audit_context,min_confirm_gate,confirm_gate,
  submission_readiness_review,validate_p208_l3_readiness,final_submission_pack,triage_write,report_generator}.py`,
  `scripts/dashboard.py`, `config/{runtime_policy,agent_policy,active_audit}.json`, `L3_READINESS_SCHEMA.json`.
- **Audit working substrate (expected to grow):** `audits/zetachain-2023-10-holdout/output/*`, `…/data/triage/*`,
  `…/data/findings/*`, `…/pocs/p215/*` — snapshot START, preserve pre-staged blind bundles.
- **New research artifacts:** `output_research/l3_readiness/ZETA-*.json`; `output_research/dry_run_submission_queue/*`.
- **Deliverables dir:** `documentation/research/assisted_mode/p215_full_funnel_rehearsal/` — P215_PLAN.md,
  PRE_RUN_SAFETY_CHECK.md, INTEGRITY_PRECHECK.md, TARGET_SELECTION.md, TARGET_INTAKE.md, COVERAGE_MANIFEST.md,
  CANDIDATE_REGISTER.json, TRIAGE_RESULTS.md, DEEP_TRACE_RESULTS.md, CONFIRM_GATE_RESULTS.md,
  SUBMISSION_READINESS_RESULTS.md, L3_READINESS_RESULTS.md, HARNESS_RESULTS.md, REPORT_PACKAGES/,
  DRY_RUN_SUBMISSION_QUEUE/, DASHBOARD_REVIEW.md, FREEZE_MANIFEST.md, ANSWER_KEY_SCORECARD.md, FINDING_MATCHES.md,
  MISSES_AND_FALSE_POSITIVES.md, SEVERITY_CALIBRATION.md, L3_EFFECTIVENESS.md, FUNNEL_EFFECTIVENESS.md,
  DRY_RUN_QUEUE_AUDIT.md, HUMAN_REVIEW_QUEUE.md, FAILURE_CASES.md, P215_RECOMMENDATION.md, metrics.json,
  integrity_checks.md.

## Verification
- Production files byte-identical START==END (md5 first-8 table in integrity_checks.md).
- `config/active_audit.json` restored to `quantamm-2024-12-eval`; `AUDITWATCH_L3_READINESS` unset at END.
- Flag-on funnel: every High in the dry-run queue has L3 PASS or a written override; 0 source-refuted candidates routed;
  Mediums need source-proven impact; **0 false queue entries** after scoring (target).
- Answer key opened only after FREEZE_MANIFEST hash recorded.
- Dashboard exposes **no** submit/promote controls; 0 stray dashboard processes; all JSON valid.

## Decision space
End with exactly one: `FULL_FUNNEL_REHEARSAL_READY_FOR_REAL_HUNT` (expected if funnel routes correctly, L3 blocks
inflated Highs without under-rating real ones, dry-run queue clean, packages triager-ready, dashboard matches state,
hashes byte-identical, quantamm restored) · `FULL_FUNNEL_REHEARSAL_PARTIAL` · `FULL_FUNNEL_REHEARSAL_FAILED_L3` ·
`FULL_FUNNEL_REHEARSAL_FAILED_ROUTING` · `FULL_FUNNEL_REHEARSAL_FAILED_PACKAGE_READINESS` ·
`HUNT_ABORTED_TOOLING_RISK` · `HUNT_ABORTED_SCOPE_RISK` · `INVALID_RUN`.

## Follow-on (NOT this phase)
Enable the L3 flag on a genuinely live hunt; P212 conversion-family sibling-parity lens (002-M eETH near-miss); a
dedicated recall sweep (the bounded discovery here will under-count zetachain's 48 findings by design).
