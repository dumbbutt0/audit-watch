# P219 — ZETA FIELD SOURCE MAP (desired field → best artifact)

Implemented in `scripts/sync_hunt_findings.build_bundle` with a `src(field, value, path)` recorder that writes
`_field_provenance[field] = {path, blind_evidence:true}` ONLY when the value is artifact-backed (HARD RULE).

| Dashboard field | Source artifact | Notes |
|---|---|---|
| title / affected_contracts / affected_functions / function_map / attacker_model / loss_type | CANDIDATE_REGISTER.json | the blind register surface |
| summary / mechanism / root_cause / exploit_steps | merged_findings.json (description, impact, ice_chain.exploit_path, ite.intent) | |
| reachability_verdict | confirm/reachability_analysis.json (reachability_status) | refined by register attacker_model |
| PoC actual (vulnerable_output) / expected+control (corrected_output, control_case) / value-delta (runtime_delta) / corrected_reference_type | output_research/l3_readiness/<id>.json (actual_delta, expected_delta_or_control, magnitude_basis, dependency_mocks) | present iff the L3 record recorded them (executed ⇒ full) |
| who_loses / asset_or_value / limitations | L3 record (victim_or_protocol_loss, affected_asset_or_state, source_validity_notes) | who_gains stays unknown unless an artifact names a beneficiary |
| defense_map | triage follow_up_packet → L3 expected_delta_or_control → merged.recommendation | the recommended fix = the missing defense |
| intent_scope_operator_assumptions | register (privileged⇒operator-dep) / triage decision_reason | |
| main_blocker / l3_status / high_promotion_allowed | L3 record + validate_p208.decide() (flag-on, server-side) | |
| final_triager_decision | triage (triage_status, decision_reason) | |
| red_flags | derived from recorded facts (attacker_model, l3_status, control present, production_source_modified, reachability) | each red flag cites its evidence path |
| evidence_backup / source_refs | register + merged + confirm + L3 + harness(poc_path) + report-package + dry-run-queue | |
| conversion_classification / scoring_note / last_reviewer_note | answer-key scorecard + FINDING_MATCHES — **POST-SCORE ONLY** | PRIMARY mention drives conversion; grouped mentions are note-only; never a blind-evidence source |
| novelty_duplicate | **no artifact → unknown / HUMAN_PENDING** | not invented |
