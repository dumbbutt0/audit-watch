# P209 — L3 gate interface (P208 → confirm path)

The interface is the **pure function** `decide(record)` already implemented in `scripts/validate_p208_l3_readiness.py`
(P208), reading an `L3_READINESS_SCHEMA.json` record. P210 would call it from `submission_readiness_review.py` only.
This document fixes the contract; it changes no code.

## Inputs (required L3 readiness record fields — from the P208 schema)
`candidate_id` · `threat_ceiling` · `l3_status` · `poc_tier` · `poc_path` · `poc_command` · `poc_result` ·
`actual_delta` · `expected_delta_or_control` · `affected_asset_or_state` · `attacker_model` ·
`victim_or_protocol_loss` · `magnitude_basis` · `source_validity_notes` · `dependency_mocks` ·
`production_source_modified` · `research_only:true` · `routes_in_production:false`.
Join key: `candidate_id` ↔ finding_id (triage `recommended_severity` supplies the severity target).

## Outputs produced (advisory; consumed by the readiness overlay + dashboard)
| field | meaning |
|---|---|
| `l3_status` | PASS / FAIL / NEEDS_HARNESS / NOT_ATTEMPTED / HUMAN_OVERRIDE (echoed) |
| `poc_tier` | L1_STATIC_TRACE / L2_UNIT_HARNESS / L3_REAL_CONTRACT_POC / HUMAN_EQUIVALENT / NONE |
| `high_promotion_allowed` | bool, from `decide()` |
| `high_promotion_blocker` | human-readable blocker string (empty if allowed) |
| `calibrated_severity_after_l3` | high / medium / needs_harness_for_severity / invalid |
| `submission_blocker_codes` | [] or one of: `blocked_by_missing_l3_poc`, `blocked_by_insufficient_impact`, `blocked_by_source_refutation` |
| `human_override_required` | bool — true when target=High & l3_status∉{PASS,HUMAN_OVERRIDE} |
| `human_override_reason` | written rationale string when `l3_status==HUMAN_OVERRIDE`; else "" |
| `evidence_summary` | one line: poc_path + actual_delta + control |

## Failure states
- `l3_status==FAIL` → `calibrated_severity_after_l3 ∈ {medium, invalid}`; `submission_blocker_codes` includes
  `blocked_by_source_refutation` if source-refuted, else `blocked_by_insufficient_impact`.
- `l3_status∈{NOT_ATTEMPTED, NEEDS_HARNESS}` for a High target → `blocked_by_missing_l3_poc`.
- malformed record / schema-fail → treated as **NEEDS_HARNESS for a High target** (fail-closed for High readiness;
  see missing-field handling).

## Missing-field handling
- **Fail-closed for HIGH readiness:** absence/blank of any condition field ⇒ `high_promotion_allowed=false`
  (a High can never become submission-ready by omission).
- **Fail-open everywhere else:** a missing L3 record does NOT block Medium readiness, does NOT suppress discovery,
  does NOT block candidate creation or the existing gates; the candidate simply carries
  `l3_status=NOT_ATTEMPTED → NEEDS_L3_HARNESS` for display.

## Schema delta vs P208
Add (optional, derived) output fields to the record on write-back: `calibrated_severity_after_l3`,
`submission_blocker_codes`, `human_override_required`, `human_override_reason`, `evidence_summary`,
`severity_target` (from triage). No change to required inputs. All remain `research_only:true`/`routes_in_production:false`.
