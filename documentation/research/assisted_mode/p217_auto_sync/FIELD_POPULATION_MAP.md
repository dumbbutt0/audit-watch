# P217 — FIELD POPULATION MAP (source → synced field)

Programmatic extraction in `scripts/sync_hunt_findings.py:build_bundle()`. Rule: populate only from a real artifact;
absent ⇒ leave `unknown` / `MISSING_EVIDENCE`. **Never invent.**

| Synced field | Source artifact → value |
|---|---|
| `title` | CANDIDATE_REGISTER.title |
| `summary` / `impact` | merged_findings.impact → ice_chain.impact → description → register.title |
| `affected_contracts` / `affected_functions` | register.contract / register.function (merged.location cross-check) |
| `mechanism` / `suspected_mechanism` | merged_findings.description (the one-sentence mechanism) |
| `root_cause` | merged_findings.ite.intent → L3.source_validity_notes |
| `attacker_model` | register.attacker_model (mapped to a sentence: permissionless/privileged/conditional) |
| `exploit_steps` | merged_findings.ice_chain.exploit_path, split on `->`/`→`/sentence boundary |
| `function_map` | `{role: impact_class, function, permission: attacker_model, why: description, source: file:lines}` |
| `defense_map` | triage.follow_up_packet → L3.expected_delta_or_control → merged.recommendation (the recommended fix = the missing defense) |
| `poc_verification` | L3.poc_path / poc_command / poc_result; `poc_status=REPRODUCED` iff L3.l3_status==PASS & poc_path present (e.g. ZETA-07) |
| `impact_and_severity` | merged.impact + triage.recommended_severity + L3.calibrated_severity_after_l3 + register.claimed_severity |
| `intent_scope_operator_assumptions` | privileged⇒operator/admin-dependency note; else triage.decision_reason |
| `novelty_duplicate` | **no source → `unknown`** (honest gap) |
| `conversion_classification` / `conversion` | scorecard PRIMARY verdict (FINDING_MATCHES `## <id>` header or bolded `**<id>**` cell): HIT→CLEAN_HIT, PARTIAL→STRONG_PARTIAL, ADJACENT→ADJACENT, TRUE_NEGATIVE/rejected→REJECTED, MISS/none→NONE |
| `main_blocker` / `l3_status` / `high_promotion_allowed` / `high_promotion_blocker` | L3 record + `validate_p208.decide()` (flag-on, read-only) |
| `final_triager_decision` | triage.triage_status + decision_reason |
| `red_flags` | derived from recorded fields only (attacker_model ⇒ admin-only-call check; L3 ⇒ executed-PoC & control checks); status `pass/fail/manual`, never fabricated |
| `evidence_backup` / `source_refs` | register file:lines + merged manifest + L3 record + harness (poc_path) + dry-run-queue + scorecard |
| `dry_run_queue` | dry_run_submission_queue/<id>.json.readiness_state |
| `last_reviewer_note` (post-score) | scorecard/FINDING_MATCHES line(s) mentioning the id (verbatim; grouped mentions never set the conversion) |

## Misattribution guard
Scorecard verdicts set `conversion` ONLY from a **primary** mention (per-id `## <id>` header or bolded `**<id>**`
cell). Grouped/parenthetical mentions (e.g. "examined fn in ZETA-07/08", "ZETA-10/ZETA-12 same contracts") appear in the
human-readable note but do **not** drive the conversion — so ZETA-07 is not mislabelled a MISS from the M-28 row.
