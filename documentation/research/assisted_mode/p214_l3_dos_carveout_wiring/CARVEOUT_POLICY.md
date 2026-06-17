# P214 — carve-out policy (as implemented)

Implemented in `scripts/validate_p208_l3_readiness.py`: `_apply_dos_carveout()` + a flag-guarded post-step in
`decide()`. **Default-off; `decide()` flag-off is byte-identical to pre-P214** (no carve-out keys, no severity change).

Flag-on, `repaired = high` iff ALL hold:
- `dos_carveout_candidate is True`; base `calibrated_severity == "medium"`;
- none of the never-upgrade guards: `"refut" in source_validity_notes`; `production_source_modified is True`;
  `l3_status ∈ {NOT_ATTEMPTED, NEEDS_HARNESS}`; `dos_carveout_human_judgment_required` set but `dos_carveout_notes` empty;
- ALL 10 criteria `is True` (executed_l3_harness, deterministic_failure, core_protocol_path, supported_asset_or_path,
  no_practical_workaround, permissionless_or_normal_user_trigger, affects_user_class_or_protocol_function,
  not_self_inflicted_only, control_case_demonstrates_expected_success, no_trusted_admin_prereq).
Else: no upgrade; emits `dos_carveout_missing_criteria` + `dos_carveout_blocker`. **No broad "DoS == High".**

Human-judgment criteria (`no_practical_workaround`, `supported_asset_or_path`, `affects_user_class_or_protocol_function`,
`not_self_inflicted_only`) must be explicit booleans set by a human; when `dos_carveout_human_judgment_required=true`
a written `dos_carveout_notes` is required (no silent inference from prose).

Output (flag-on): `dos_carveout_evaluated`, `dos_carveout_applied`, `dos_carveout_missing_criteria`,
`dos_carveout_blocker`, `dos_carveout_notes`, `calibrated_severity_after_l3`. `submission_readiness_review.l3_evaluate`
and `dashboard /api/p212` pass these through read-only.
