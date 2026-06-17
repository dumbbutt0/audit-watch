# P208 — Operationalize the L3 HIGH bar as a dry-run severity policy

## Context
The L3 realized-impact HIGH standard is now validated on two independent corpora (P204 decent: H-01 setRouter→mint
HIGH_CONFIRMED, M-03 demoted; P207 vultisig: H-01 claim-fee-loss HIGH_CONFIRMED, M-03 cap-bypass demoted). P208 turns
that principle into an **operational dry-run policy**: a candidate may only reach `HIGH_CONFIRMED` with a passing
L1/L2/L3 PoC (or reproducible-equivalent / written human override); otherwise it is calibrated down or marked
`NEEDS_HARNESS_FOR_SEVERITY`. This phase is **dry-run only** — no auto-submit, no live routing, no promotion/demotion
of real findings, no change to canonical labels or answer keys.

## Recon (read-only) — align with existing infra, keep production byte-identical
- **Existing pattern to mirror exactly:** `scripts/submission_readiness_review.py` — research-only, un-wired,
  append-only readiness OVERLAY that NEVER flips `submission_ready`/`routing_allowed`, fail-open, with states
  including `blocked_by_missing_poc` / `blocked_by_missing_impact`. The L3 policy maps onto these states.
- **Existing severity vocab:** `schemas/severity_calibration.schema.json` (`calibrated_severity` enum
  critical/high/medium/low/qa/invalid; `calibration_source` already has `poc_informed`); PoC shapes in
  `schemas/poc_result.schema.json` / `poc_validation.schema.json`.
- **Un-wired validator family:** `scripts/validate_pNNN.py` (offline, research-only) — the established home for a
  dry-run helper. `config/runtime_policy.json api_free=true` → no live submission route enabled.
- **Decision:** do NOT edit production prompts/`deep_trace.md`/checker/router/ledger/detector/dashboard (campaign
  integrity discipline; the brief permits this choice). The policy ships as a **standalone dry-run validator +
  schema + docs**, carrying `research_only:true` / `routes_in_production:false` markers per the platform hard rule.

## Core policy (encoded in the validator)
Static deep-trace verdict = **threat ceiling**, not final severity. `high_promotion_allowed = true` ONLY if:
`l3_status ∈ {PASS, HUMAN_OVERRIDE}` AND concrete affected asset/state AND material delta demonstrated AND attacker
model permissionless/program-accepted AND `production_source_modified == false` AND mocks don't create the vulnerable
condition AND a control/expected-vs-actual comparison is present. Else `false` with a `high_promotion_blocker`.
Demotion mapping: valid mechanism w/o realized High impact → `MEDIUM_OR_LOWER_CALIBRATED`; static capability-only →
not reportable as High; unproven magnitude → `NEEDS_HARNESS_FOR_SEVERITY`; DoS/griefing/precision/local/bounded →
Medium unless L3 proves permanent material loss/insolvency.

## Required evidence fields (schema)
`l3_status` (PASS/FAIL/NEEDS_HARNESS/NOT_ATTEMPTED/HUMAN_OVERRIDE) · `poc_tier` (L1_STATIC_TRACE/L2_UNIT_HARNESS/
L3_REAL_CONTRACT_POC/HUMAN_EQUIVALENT/NONE) · `poc_path` · `poc_command` · `poc_result` · `actual_delta` ·
`expected_delta_or_control` · `affected_asset_or_state` · `attacker_model` · `victim_or_protocol_loss` ·
`magnitude_basis` · `source_validity_notes` · `dependency_mocks` · `production_source_modified` (bool) ·
`high_promotion_allowed` (bool, derived) · `high_promotion_blocker`.

## Execution sequence (when approved)
Work dir: `documentation/research/assisted_mode/p208_l3_high_policy_dryrun/`.

1. **Integrity precheck** (`INTEGRITY_PRECHECK.md`): START md5-first-8 for `prompts/deep_trace.md` (`ef93a6c2`),
   `scripts/validate_deep_pass_mechanisms.py` (`5d2a97f9`), `scripts/eval_locus_resolver.py` (`3b0b2c02`), hermes
   ledger (`fc446040`); note no dashboard/schema production files will be modified; confirm P204
   (`p204_l3_magnitude_standard/metrics.json`) + P207 (`p207_…/metrics.json`) evidence exist; confirm `api_free=true`
   / no live submission route.
2. **Policy spec** `L3_HIGH_POLICY.md`: threat-ceiling-vs-final-severity, L1/L2/L3 tiers, evidence fields, the
   HIGH_CONFIRMED promotion rule, demotion/NEEDS_HARNESS rules, human-override requirements (written rationale),
   non-submission guarantee.
3. **Schema** `L3_READINESS_SCHEMA.json` (draft-07): required evidence fields + enums; aligns vocab with
   `severity_calibration.schema.json`; carries `research_only`/`routes_in_production:false`.
4. **Dry-run validator** `scripts/validate_p208_l3_readiness.py` (un-wired helper, mirrors validate_pNNN.py +
   submission_readiness_review invariants): `validate <record.json>` (schema + required-field check),
   `decide` (compute `high_promotion_allowed` + `high_promotion_blocker` + `calibrated_severity` +
   `display_readiness` mapped to submission_readiness states), `backtest` (run the fixtures, emit metrics). Prints a
   per-candidate readiness panel: threat ceiling · calibrated severity · L3 readiness · PoC status ·
   high_promotion_allowed · blocker · submission readiness. Submits/routes NOTHING.
5. **Backtest fixtures** `backtest/*.json` — L3 readiness records built from P204/P207 evidence: decent **H-01**
   (PASS, L3_REAL_CONTRACT_POC, real DcntEth, 1e6-ether unbacked mint, control present, prod unmodified) → allow;
   decent **M-03** (FAIL/NEEDS_HARNESS, no material theft) → block; vultisig **H-01** (PASS, faithful pool, B loses
   fees, control) → allow; vultisig **M-03** (cap-bypass, no theft) → block. `BACKTEST_SCORECARD.md`.
6. **Regression fixtures** `regression/*.json` + `REGRESSION_CHECKS.md`: static HIGH_THREAD no PoC
   (NOT_ATTEMPTED) → blocked; DoS/griefing Medium (no permanent loss) → blocked from High; precision/rounding w/o
   magnitude_basis → NEEDS_HARNESS/Medium; source-refuted (FAIL) → blocked. (Reuse decent-06 false-High +
   decent-12 NEEDS_HARNESS from P204 as real regression rows.)
7. **Submission readiness linkage** `SUBMISSION_READINESS_LINKAGE.md`: map L3 outcomes onto the EXISTING
   `submission_readiness_review.py` states (HIGH pkg requires `l3_status PASS`/override else `blocked_by_missing_poc`;
   Medium pkg may proceed if mechanism+impact source-proven; NEEDS_HARNESS cannot be High-submission-ready; human
   review stays mandatory; draft allowed). Documented linkage only — NOT wired.
8. **Metrics** `metrics.json`: candidates tested, expected pass/fail matches, blocked static Highs, allowed L3 Highs,
   false-allows, false-blocks, schema validation pass/fail, dashboard/readiness mismatches.
9. **Deliverables + decision** (`DRY_RUN_INTEGRATION.md`, `P208_RECOMMENDATION.md`, `integrity_checks.md`, copy plan
   to `P208_PLAN.md`) + END integrity re-check + memory.

## Decision space
`L3_POLICY_DRY_RUN_READY` (policy operationalized dry-run only; 4 P204/P207 controls classify correctly; static High
w/o PoC blocked; schema validates; linkage explicit; production byte-identical) · `L3_POLICY_PARTIAL` ·
`L3_POLICY_BLOCKED_INTEGRATION` · `L3_POLICY_FAILED_REGRESSION` · `INVALID_RUN`. **Expected:** `DRY_RUN_READY`.

## Acceptance criteria
Dry-run only, no auto-submit/live routing; HIGH promotion requires L3 PASS or human override; decent+vultisig H-01 →
allow, M-03 → block; static High w/o PoC blocked; schema validates required fields; submission-readiness linkage
explicit; production hashes byte-identical START==END (`ef93a6c2`/`5d2a97f9`/`3b0b2c02`/ledger `fc446040`); JSON valid;
`research_only:true`/`routes_in_production:false` on every artifact; fabrication_rate=0.

## Deliverables
`P208_PLAN.md` · `INTEGRITY_PRECHECK.md` · `L3_HIGH_POLICY.md` · `L3_READINESS_SCHEMA.json` ·
`DRY_RUN_INTEGRATION.md` · `BACKTEST_SCORECARD.md` · `SUBMISSION_READINESS_LINKAGE.md` · `REGRESSION_CHECKS.md` ·
`P208_RECOMMENDATION.md` · `metrics.json` · `integrity_checks.md` · `scripts/validate_p208_l3_readiness.py`
(un-wired) · `backtest/*.json` · `regression/*.json`. Memory: `project_phase208_*` + one-line MEMORY.md pointer.

## Verification
`python scripts/validate_p208_l3_readiness.py backtest` → 4/4 controls match expected (decent/vultisig H-01 allow,
M-03 block) + all regression rows blocked/needs-harness as specified, 0 false-allows / 0 false-blocks; schema
validation passes on all fixtures; `metrics.json` valid JSON; production hashes byte-identical at END; every emitted
artifact carries `research_only:true`/`routes_in_production:false` and nothing is submitted/routed.

## Follow-on (NOT this phase)
If `DRY_RUN_READY`: a later human decision on whether/how to wire the L3 gate into the real submission-confirm path
(cost model: auto-scaffold L2/L3 harness vs human-authored; where it sits vs the existing `min_confirm_gate`/
`confirm_gate`). Deep-pass recall + oracle track remain separate.
