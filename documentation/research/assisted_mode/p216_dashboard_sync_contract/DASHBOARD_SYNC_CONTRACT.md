# P216 — DASHBOARD SYNC CONTRACT

**Adapter:** `scripts/dashboard_sync.py` — `to_synced_finding(bundle) -> dict` (pure, no I/O).

## Inputs (a candidate bundle; every key optional)
`candidate_id` · `source_track` ∈ {audit_workspace,funnel,runtime,detector,campaign,l3,dry_run_queue} · `subject`/
`workspace_or_audit` · `phase_discovered` · `contract`/`function`/`contract_function` · `title`/`summary`/`impact` ·
`threat_ceiling`/`claimed_severity` · `conversion` · `poc` {poc_status,test_file,test_command,vulnerable_result} ·
`triage` {recommended_severity,triage_status} · `l3` {l3_status,high_promotion_allowed,high_promotion_blocker,
calibrated_severity_after_l3} · `mechanism`/`suspected_mechanism` · `mechanism_correctness` · `severity_gate` ·
`attacker_model` · `exploit_steps` · `defense_map` · `function_map` · `intent_scope_operator_assumptions` ·
`red_flags` · `novelty_status` · `reachability_verdict` · `vulnerable_output` · `limitations` · `blocker_reason` ·
`dry_run_queue` {readiness_state} · `report_package` · `source_refs`/`artifact_links` · `scoring_note` (post-answer-key
only) · `p155_gate1_source_intent` · `p155_gate2_attacker_model`.

## Output
One record in `SYNCED_FINDING_SCHEMA.json` (schema `synced-1`) that is **also a valid funnel-1 record**, so:
- `funnel.load_records()` (after the P216 merge) ingests it → `/funnel`, `/findings`, `/candidates`.
- `finding_detail.build_verifier_evidence()` renders the full card from its fields (mechanism, function_map, attacker,
  defense_map, exploit steps, severity args, impact, red flags, conversion, blocker, evidence_completeness).

## Mapping rules (the contract)
1. **Missing → explicit.** Absent scalar → `"unknown"`; absent list section → `["MISSING_EVIDENCE"]`; absent PoC result
   → `MISSING_EVIDENCE`. Never fabricated.
2. **No inferred severity.** `severity_recommendation` = first **recorded** severity among
   `triage.recommended_severity`, `l3.calibrated_severity_after_l3` (if a real severity), `severity_recommendation`;
   else `None` → the card's `_sev_or_status` shows `HUMAN_PENDING`. A conversion/decision token is **never** placed in a
   severity slot (`validate_synced` rejects it).
3. **No computed readiness beyond derived package status.** `submission_package_status_derived` is a display label
   (default `NOT_READY`); the canonical `submission_ready` stays **false**; `canonical_submission_ready_source` names the
   machine-owned gate (`submission_gate.py`).
4. **Safety constants (always):** `research_only:true`, `review_only:true`, `routes_in_production:false`,
   `routing_allowed:false`, `submission_ready:false`, `human_review_required:true`, `no_submit_controls:true`,
   `browser_computes_severity:false`. `validate_synced()` fails the record if any drift.
5. **Enum clamping (funnel-1 compatibility):** `conversion`→{CLEAN_HIT,STRONG_PARTIAL,ADJACENT,REJECTED,ABSTAINED,NONE}
   (default NONE); `poc.poc_status`→{NOT_STARTED,IN_PROGRESS,REPRODUCED,PARTIAL_REPRO,NOT_REPRODUCED} (default
   NOT_STARTED); `submission.submission_status`→{NOT_STARTED,…} (default NOT_STARTED).
6. **L3 surfaced:** `l3_status`, `high_promotion_allowed`, `high_promotion_blocker` copied through; `main_blocker`
   prefers `blocker_reason` then the L3 blocker.
7. **Post-score notes** ride in `last_reviewer_note` / `raw_fields` only — never as a severity or a routing signal.

## Validation
`validate_synced(rec)` returns `[]` when: schema id ok; required identity present; enums valid; **all 8 safety flags
hold**; `severity_recommendation` is a recorded severity or `HUMAN_PENDING`. The generator refuses to write any record
that fails.

## Idempotence / reversibility
Records keyed by `record_id`; the generator removes prior records with the same prefix before writing → no duplicates,
re-runs byte-identical. Output is a standalone mirror file (`synced_findings.generated.json`) — deletable to revert.
