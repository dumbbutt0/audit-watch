# P214 — Wire the deterministic core-path DoS carve-out into decide() behind AUDITWATCH_L3_READINESS

## Context
P213 validated (research-only) a narrow 10-criterion carve-out that fixes the P212 under-rating (SOPH-03 = official
High but L3 mapping said Medium because impact=DoS), with 0 new false-Highs. P214 implements it into the real L3 path
(`validate_p208_l3_readiness.decide()` + schema + readiness + tests) **behind the existing default-off
`AUDITWATCH_L3_READINESS` flag**. No "DoS = High" — only an L3-proven deterministic DoS of a core supported path,
all 10 criteria + never-upgrade guards.

## Recon (read-only) — exact integration point
- `scripts/validate_p208_l3_readiness.py` `decide(rec)` (pure) computes `cal`/`allowed` and returns a fixed dict.
  SOPH-03 hits `l3=="FAIL" → cal="medium"`. `os` not imported there yet.
- `decide()` consumers: P208 backtest (research), `submission_readiness_review.l3_evaluate` (P210; flag-gated upstream),
  `validate_p213` (research), dashboard `/api/p212` (read-only display). So a **flag-guarded** post-step inside
  `decide()` keeps flag-off byte-identical for ALL of them.
- `submission_readiness_review.l3_evaluate` already maps `decide()["calibrated_severity"]` → `calibrated_severity_after_l3`.
- Tests: `tests/research/test_l3_readiness.py` (20), `tests/research/test_submission_readiness.py` (14). Existing
  flag-on tests use records WITHOUT carve-out fields → carve-out won't trigger → they stay green.

## Design (flag-off output-equivalent to pre-P214)
In `validate_p208_l3_readiness.py`: add `import os`, `_l3_flag_on()` (mirror submission_readiness_review), and a pure
`_apply_dos_carveout(rec, cal, allowed, notes) -> (carveout_fields, cal2, allowed2)`. In `decide()`, after building the
base `result`, **only when `_l3_flag_on()`**: run the carve-out, update `calibrated_severity`/`high_promotion_allowed`/
`submission_state`/`high_promotion_blocker`, and merge the carve-out fields. Flag-off → return the unchanged pre-P214
dict (no carve-out keys).

`_apply_dos_carveout` upgrades to `high` iff: `rec.dos_carveout_candidate` is true AND base `cal=="medium"` AND none of
the never-upgrade guards fire (`"refut" in notes`; `production_source_modified`; `l3_status ∈ {NOT_ATTEMPTED,NEEDS_HARNESS}`;
`dos_carveout_human_judgment_required` set but `dos_carveout_notes` empty) AND ALL 10 criteria are `is True`:
`executed_l3_harness, deterministic_failure, core_protocol_path, supported_asset_or_path, no_practical_workaround,
permissionless_or_normal_user_trigger, affects_user_class_or_protocol_function, not_self_inflicted_only,
control_case_demonstrates_expected_success, no_trusted_admin_prereq`. Else no upgrade + `dos_carveout_missing_criteria`
+ `dos_carveout_blocker`. Output (flag-on): `dos_carveout_evaluated`, `dos_carveout_applied`,
`dos_carveout_missing_criteria`, `dos_carveout_blocker`, `dos_carveout_notes`, `calibrated_severity_after_l3`.

## Files
1. **`documentation/research/assisted_mode/p208_l3_high_policy_dryrun/L3_READINESS_SCHEMA.json`** — additively add the
   optional carve-out fields (13: candidate + 10 criteria + notes + human_judgment_required). Existing records stay valid.
2. **`scripts/validate_p208_l3_readiness.py`** — `import os` + `_l3_flag_on()` + `_apply_dos_carveout()` + flag-guarded
   post-step in `decide()`.
3. **`scripts/submission_readiness_review.py`** — `l3_evaluate()` passes through the new `dos_carveout_*` fields from
   the `decide()` result (additive).
4. **`output_research/l3_readiness/SOPH-03.json`** — add the carve-out evidence block (all 10 true,
   `dos_carveout_candidate=true`, `human_judgment_required=true` + `dos_carveout_notes`). (Live readiness record, not a
   frozen blind candidate.)
5. **`scripts/dashboard.py`** `/api/p212` — additively surface `dos_carveout_applied` per row (read-only); optional
   `dashboard/p212.html` badge.
6. **`tests/research/test_l3_dos_carveout.py`** (new) + fixtures.

## Tests / verification
- Flag-OFF: `decide()` on the updated SOPH-03 record → `medium`, NO carve-out keys (byte-equivalent); existing
  `test_l3_readiness.py` (20) + `test_submission_readiness.py` (14) green; P208 backtest 10/10.
- Flag-ON (`AUDITWATCH_L3_READINESS=1`): SOPH-03 → `high`, `dos_carveout_applied=true`; one-criterion-missing → medium;
  munchables/no-harness (NEEDS_HARNESS) → not upgraded; source-refuted → invalid; production_source_modified → not
  upgraded; human_judgment_required w/o notes → not upgraded; malformed/missing → fail closed; decent M-03 / vultisig
  M-03 / decent-06 → stay < High; static-High-no-PoC → blocked. **0 new false-Highs.**
- Re-run P213 `validate_p213.py` (still 10/10). No submit/route/promote. `grep` confirms no new production wiring beyond
  the flag-gated decide() path.

## Deliverables
`P214_PLAN.md` · `INTEGRITY_PRECHECK.md` · `IMPLEMENTATION_NOTES.md` · `SCHEMA_CHANGELOG.md` · `CARVEOUT_POLICY.md` ·
`TEST_RESULTS.md` · `BACKTEST_RESULTS.md` · `CARVEOUT_SCORECARD.md` · `FAILURE_CASES.md` · `P214_RECOMMENDATION.md` ·
`metrics.json` · `integrity_checks.md` (under `documentation/research/assisted_mode/p214_l3_dos_carveout_wiring/`).
Code: `validate_p208_l3_readiness.py`, `submission_readiness_review.py`, `dashboard.py`, `L3_READINESS_SCHEMA.json`,
`output_research/l3_readiness/SOPH-03.json`, `tests/research/test_l3_dos_carveout.py`.

## Decision space
`DOS_CARVEOUT_DARK_WIRING_READY` (flag-off unchanged; SOPH-03→High flag-on only-with-all-10; 0 new false-Highs; all
controls hold; P210/P208/P213 green; deep_trace/min_confirm/confirm_gate byte-identical START==END) ·
`DOS_CARVEOUT_PARTIAL` · `DOS_CARVEOUT_FAILED_FALSE_HIGH` · `DOS_CARVEOUT_FAILED_TO_FIX_SOPH03` ·
`DOS_CARVEOUT_FAILED_REGRESSION` · `INVALID_RUN`. **Expected:** `DARK_WIRING_READY`.

## Acceptance criteria
Behind `AUDITWATCH_L3_READINESS`; flag-off output-equivalent; SOPH-03 → High only with all 10; missing criterion blocks;
decent/vultisig stay < High; source-refuted can't upgrade; static-High-no-PoC blocked; existing P210 tests pass;
P208/P213 regressions pass; no route/submit/promote side effects; `deep_trace.md`/`min_confirm_gate.py`/`confirm_gate.py`
byte-identical START==END; changed files' hashes recorded; JSON valid; human review still mandatory.

## Follow-on (NOT this phase)
Enable the flag on a real hunt; P212 conversion-family sibling-parity lens (002-M near-miss); recall sweep.
