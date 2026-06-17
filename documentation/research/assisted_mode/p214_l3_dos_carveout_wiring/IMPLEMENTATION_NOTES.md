# P214 — implementation notes

## Files changed (production)
- `scripts/validate_p208_l3_readiness.py` `7e148e18 → fe37e6ad` — `import os`; `_l3_flag_on()`;
  `_DOS_CARVEOUT_CRITERIA`; pure `_apply_dos_carveout()`; flag-guarded post-step in `decide()` (flag-off returns the
  unchanged pre-P214 dict).
- `scripts/submission_readiness_review.py` `7c4b563d → e4960878` — `l3_evaluate()` passes through `dos_carveout_evaluated/
  applied/blocker/missing_criteria` from the `decide()` result (additive).
- `scripts/dashboard.py` `dbed5174 → 197ac4d5` — `/api/p212` adds read-only `dos_carveout_applied` per row.
- `documentation/.../p208_l3_high_policy_dryrun/L3_READINESS_SCHEMA.json` `91c0590f → 415d3eeb` — additive carve-out fields.

## Files added / updated (non-production)
- `output_research/l3_readiness/SOPH-03.json` — added the carve-out evidence block (all 10 true, candidate=true,
  human_judgment_required=true + notes). Live readiness record, NOT a frozen blind candidate.
- `dashboard/p212.html` — small "DoS carve-out → High (flag on)" badge.
- `tests/research/test_l3_dos_carveout.py` (20 tests) + this deliverable set.

## Design choice (default-off equivalence)
`decide()` is pure except for one `if _l3_flag_on():` post-step. Flag-off → identical pre-P214 output for ALL records.
Flag-on → carve-out applies only to records explicitly carrying the candidate + 10 criteria, so existing flag-on tests
(records without those fields) are unaffected.

## Out of scope (unchanged, hash-verified): deep_trace.md, min_confirm_gate.py, confirm_gate.py, routing/submission.
