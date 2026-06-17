# P208 — dry-run integration

## What was integrated (lightest possible, un-wired)
- **Schema** `L3_READINESS_SCHEMA.json` (draft-07) — the evidence contract a candidate must carry to attempt
  `HIGH_CONFIRMED`; vocab aligned with `schemas/severity_calibration.schema.json`.
- **Validator** `scripts/validate_p208_l3_readiness.py` — three commands, all advisory:
  - `validate <record.json>` — JSON-schema + required-field check.
  - `decide <record.json>` — computes `high_promotion_allowed`, `high_promotion_blocker`, `calibrated_severity`,
    `submission_state`; always `human_review_required=true`; carries `research_only:true`/`routes_in_production:false`.
  - `backtest` — runs `backtest/*.json` + `regression/*.json`, scores vs each fixture's `expected`, writes
    `metrics.json`. Prints a per-candidate readiness panel: ceiling · awarded · l3_status/tier · calibrated severity
    · high_promotion_allowed · submission_state · blocker.

## What was deliberately NOT done (scope)
- No edit to `prompts/deep_trace.md`, the checker, router, ledger, detectors, or `scripts/dashboard.py`
  (production hashes byte-identical START==END).
- No wiring into `run_pipeline.sh` / `agent_policy.json` / any routing or gate. The validator is standalone.
- No auto-submit, no live routing, no promotion/demotion of real findings, no canonical-label/answer-key change.

## How a reviewer uses it (dry-run)
1. Author an L3 readiness record for a HIGH-candidate (fill the evidence fields from the PoC run).
2. `python scripts/validate_p208_l3_readiness.py validate rec.json` then `decide rec.json`.
3. Read `high_promotion_allowed` + `submission_state`; if blocked, the `high_promotion_blocker` names exactly what is
   missing (PoC, control, material delta, attacker model, source modification, or mock that creates the bug).
4. Hand off to `submission_readiness_review.py` per `SUBMISSION_READINESS_LINKAGE.md` — human review still mandatory.

## Display panel (existing dashboard, optional, not modified here)
The same `decide()` fields (threat ceiling, calibrated severity, L3 readiness, PoC status, high_promotion_allowed,
blocker, submission readiness) are display-ready and could be surfaced read-only in `scripts/dashboard.py` in a later
phase without changing behavior — left un-wired in P208.
