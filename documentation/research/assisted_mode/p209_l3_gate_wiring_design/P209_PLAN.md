# P209 — L3 HIGH gate wiring DESIGN for the submission-confirm path (design-only)

## Context
P208 shipped the L3 realized-impact HIGH standard as a dry-run, un-wired policy (`scripts/validate_p208_l3_readiness.py`
+ `L3_READINESS_SCHEMA.json`): HIGH requires L3 PASS or human override; deep-trace severity is only a threat ceiling;
Medium may proceed if source-proven; NEEDS_HARNESS can't be High-submission-ready; backtest 10/10, 0 false-allow/0
false-block. P209 designs **where/how** that policy should wire into the real submission-confirm path — **design only,
no wiring, no production behavior change** (only read-only inspection + the existing P208 read-only backtest probe).

## Recon already done (read-only) — the real confirm path is mapped
- `data/triage/{submit,poc_required}.jsonl` ← triage; consumed downstream.
- **`scripts/min_confirm_gate.py`** — deterministic FIELD-PRESENCE gate on the submit/poc_required buckets
  (entrypoint/manifest_refs/preconditions/impact/guards/PoC-plan/severity-ceiling/confidence/dup-reason);
  writes `output/min_confirm_gate.json`; override `AUDITWATCH_MINCONFIRM_OVERRIDE=1`.
- **`scripts/confirm_gate.py`** — deterministic REACHABILITY-TRUTH gate; `--mode eval` warns/exit0,
  `--mode submission` HARD-FAILs non-credible High/Critical, `--strict` extends to Medium/uncertain; reads
  `output/confirm/reachability_analysis.json`; writes `output/confirm/confirm_gate.json`. **This is the real blocking
  precision gate.**
- `run_pipeline.sh submission-confirm` = `min_confirm_gate` then `confirm_gate --mode submission [--strict]`.
- **`scripts/submission_readiness_review.py`** — human readiness OVERLAY, research-only/append-only, `READINESS_STATES`
  incl. `blocked_by_missing_poc`/`blocked_by_missing_impact`/`blocked_by_severity_too_low`; **NEVER flips
  `submission_ready`/`routing_allowed`**. (P208 already links here.)
- `scripts/final_submission_pack.py` — reads triage submit/poc_required + merged_findings → `submission_pack.{md,json}`.
- `scripts/dashboard.py` computes a DISPLAY-only `submission_ready` (line ~398); `finding_detail.py`/`findings_overview.py`
  stamp `submission_ready:false`/`routing_allowed:false`/`research_only:true`. (api_free=true; nothing auto-routes.)
- **Conclusion:** the user's candidate/recommended **layered design (option F)** is the grounded choice — L3 as a
  severity-specific readiness blocker applied AFTER mechanism/source confirmation, canonicalized in
  `submission_readiness_review.py`, surfaced read-only in dashboard/pack; gates and discovery unchanged.

## Strict scope
No wiring; no live-routing change; no submit; no auto-promote/demote; no canonical-label change; no `deep_trace.md`
patch; no production behavior change beyond read-only probes. All source inspection read-only.

## Execution sequence (produce the 13 design deliverables under `documentation/research/assisted_mode/p209_l3_gate_wiring_design/`)
1. **`INTEGRITY_PRECHECK.md`** — START md5-first-8 for `prompts/deep_trace.md` (`ef93a6c2`),
   `scripts/validate_deep_pass_mechanisms.py` (`5d2a97f9`), `scripts/eval_locus_resolver.py` (`3b0b2c02`), hermes
   ledger (`fc446040`), `scripts/submission_readiness_review.py`, `scripts/min_confirm_gate.py`,
   `scripts/confirm_gate.py`, `scripts/dashboard.py`, `scripts/validate_p208_l3_readiness.py`,
   `p208_…/L3_READINESS_SCHEMA.json`; confirm `runtime_policy.api_free` unchanged; confirm no live route-to-submit.
2. **`CURRENT_CONFIRM_PATH.md`** — document candidate creation → min_confirm_gate (IO) → confirm_gate (IO) →
   submission_readiness_review states → dashboard readiness fields → `final_submission_pack` path; where severity is
   assigned; where `submission_ready`/`routing_allowed` are set (display-only). Text flow diagram.
3. **`L3_GATE_INTERFACE.md`** — exact P208→confirm-path interface: required inputs, output fields (`l3_status`,
   `poc_tier`, `high_promotion_allowed`, `high_promotion_blocker`, `calibrated_severity_after_l3`,
   `submission_blocker_codes`, `human_override_required`, `human_override_reason`, `evidence_summary`), failure states,
   missing-field handling (fail-closed for HIGH readiness, fail-open elsewhere), JSON schema delta vs P208 schema.
4. **`WIRING_OPTIONS.md`** — evaluate placements A (before min_confirm), B (between gates), C (inside confirm_gate),
   D (inside submission_readiness_review), E (dashboard/pack only), F (layered) on: advantages · risks · recall effect ·
   severity-precision effect · failure mode · complexity · can-it-suppress-investigation · can-it-mark-High-ready-without-PoC.
5. **`RECOMMENDED_WIRING_DESIGN.md`** — recommend **F (layered)**, explicitly reject A–E. Design: L3 runs AFTER
   mechanism/source confirmation (post-confirm_gate), never before candidate creation/min_confirm_gate, never
   suppresses discovery; `submission_readiness_review.py` is the canonical High blocker (new state
   `blocked_by_missing_l3_poc` when target=High & l3_status!=PASS & no override); confirm_gate records threat_ceiling +
   candidate severity but cannot mark High submission-ready without L3; dashboard/pack show L3 read-only; human override
   explicit/written/visible.
6. **`L3_READINESS_STATE_MACHINE.md`** — states (THREAT_CEILING_HIGH, MECHANISM_CONFIRMED, NEEDS_L3_HARNESS, L3_PASS,
   L3_FAIL_MEDIUM, L3_INCONCLUSIVE, HUMAN_OVERRIDE_HIGH, HIGH_SUBMISSION_READY, MEDIUM_SUBMISSION_READY,
   BLOCKED_BY_MISSING_L3, BLOCKED_BY_INSUFFICIENT_IMPACT, BLOCKED_BY_SOURCE_REFUTATION) + allowed/forbidden transitions
   (the 4 forbidden ones enumerated in the brief).
7. **`BACKWARD_COMPATIBILITY.md`** — re-run the P208 backtest (read-only probe) to confirm P204/P207 records still
   classify; show Medium-ready packages aren't blocked for lacking L3; historical candidates not rewritten; dashboard
   still shows old findings; dry-run records coexist; no route-to-submit change. Default/migration for records without
   L3 fields (treated as NEEDS_L3_HARNESS for High target, no effect on Medium).
8. **`IMPLEMENTATION_PLAN.md`** (for P210, NOT executed) — minimal changes: add L3 fields to candidate/readiness
   record; call P208 `decide()` from `submission_readiness_review.py` only; add `blocked_by_missing_l3_poc` code; add
   read-only dashboard panel; tests/fixtures; explicit no-submit guard; old-record migration/defaults.
9. **`RISK_REGISTER.md`** — unrealistic-mock false confidence; harness cost; blocking valid Highs lacking harness;
   human-override abuse; dashboard showing ceiling as final severity; accidental route-to-submit coupling; stale L3
   artifacts; dependency-setup failures; triager disagreement on impact threshold — each with mitigation.
10. **`metrics.json`** — options compared (6), recommended (1), rejected (5), state count, forbidden transitions,
    backward-compat checks pass, production hashes unchanged, decision.
11. **`P209_RECOMMENDATION.md`** + **`integrity_checks.md`** (END==START) + copy plan → **`P209_PLAN.md`** + memory.

## Decision space
`L3_WIRING_DESIGN_READY` (path mapped; 6 options compared; F recommended + A–E rejected; state machine + override
semantics + backward-compat + implementation plan written; no wiring; hashes unchanged) · `L3_WIRING_DESIGN_PARTIAL` ·
`L3_WIRING_BLOCKED_BY_PATH_UNCERTAINTY` · `L3_WIRING_REJECTED` · `INVALID_RUN`. **Expected:** `DESIGN_READY`.

## Acceptance criteria
No wiring; confirm/submission path mapped from real code; 6 placements compared; one design chosen + alternatives
rejected; state machine (with forbidden transitions) written; implementation plan written-not-executed; human-override
semantics specified; backward-compat addressed; no production behavior change; production hashes byte-identical
START==END (`ef93a6c2`/`5d2a97f9`/`3b0b2c02`/ledger `fc446040`); JSON valid.

## Verification
Production hashes identical START==END; `python scripts/validate_p208_l3_readiness.py backtest` still 10/10 (backward
compat); `metrics.json` valid JSON; every deliverable present; no file outside `p209_…/` modified.

## Follow-on (NOT this phase)
P210 = implement the layered wiring per `IMPLEMENTATION_PLAN.md` (behind an override/default-safe path), with tests,
still gated by human review. Deep-pass recall + oracle track remain separate.
