# P214 — L3_READINESS_SCHEMA.json changelog (additive)

`91c0590f → 415d3eeb`. All additions are OPTIONAL; existing records (no carve-out fields) remain valid; missing
fields mean "no upgrade". Added under `properties`:
- `dos_carveout_candidate` (bool) — declares the record for carve-out evaluation.
- 10 criteria (bool): `executed_l3_harness`, `deterministic_failure`, `core_protocol_path`, `supported_asset_or_path`,
  `no_practical_workaround`, `permissionless_or_normal_user_trigger`, `affects_user_class_or_protocol_function`,
  `not_self_inflicted_only`, `control_case_demonstrates_expected_success`, `no_trusted_admin_prereq`.
- `dos_carveout_notes` (string) — required when `dos_carveout_human_judgment_required` is true.
- `dos_carveout_human_judgment_required` (bool).
Verified: SOPH-03 (with the new block) and DEC-M-03 (without) both `schema: PASS`.
