# P216 — Unified dashboard routing contract (one synced-finding shape for all future candidates)

## Context
P215 proved the real funnel works, but its candidates landed in the **active-audit workspace** (root `/` + `/api/state`)
while `/findings`, `/candidates`, `/funnel` read the **research tracks** (`findings_overview.load_overview()` +
`funnel.load_records()` over `funnel_records.json`) — split visibility. The finished **Abracadabra H5** runtime finding
shows the desired unified behavior: one record renders a full read-only verifier card (report summary, mechanism,
function map, attacker model, exploit steps, defense map, PoC verification, impact/severity, intent/scope, novelty,
conversion, blocker, triager decision, red flags, evidence) with safety semantics (`research_only`, `routing_allowed:
false`, `submission_ready` machine-owned, no severity computed in the browser, no submit/promote controls).

Recon facts that shape the design:
- The detail card for **every** track is built by `finding_detail.build_verifier_evidence(detail, raw, documents,
  track)` — **already invoked for funnel records** (`finding_detail.py:450`). It maps funnel fields
  (`mechanism_correctness`→mech_confirmed, `severity_gate`→sev_bearing, `impact`/`suspected_mechanism`→mechanism,
  `claimed_severity`/`severity_recommendation`→severity via `_sev_or_status` which **rejects conversion tokens**,
  `p155_gate*`→red flags/intent), and emits `MISSING_EVIDENCE`/`unknown` for absent inputs. **Severity is never
  derived; submission_ready never flipped.**
- `funnel.load_records()` (`funnel.py`) reads a single `funnel_records.json`, `normalize_record()` validates enums
  (`conversion` ∈ {CLEAN_HIT,STRONG_PARTIAL,ADJACENT,REJECTED,ABSTAINED,NONE}; `poc.poc_status`; `submission_status`;
  duplicate/scope/severity_check). It is the **single chokepoint** feeding `/funnel`, `/findings` (fo `_load_funnel`),
  and `/candidates` (fo `load_overview`).
- The three HTML pages + `candidates.js` are **read-only** (GET only; no submit/promote/forms; explicit "nothing here
  routes, sets severity, or marks anything submittable"). Confirmed.

## Decisions (user-confirmed)
- **Card parity:** make the *minimal additive* renderer edit so synced records' **inline** checklist sections render as
  distinct blocks (closest to H5).
- **P215 records:** **one-time migration** — restore `funnel_records.json` to its pre-P215 backup (8 curated records)
  and re-emit the 12 P215 candidates through the adapter into the generated mirror (no duplicates).
- **Writer location:** separate generated mirror `documentation/research/funnel/synced_findings.generated.json` +
  one additive reader merge (spec-preferred).

## Approach
1. **Canonical schema** `…/p216_dashboard_sync_contract/SYNCED_FINDING_SCHEMA.json` — superset = funnel-1 fields (so
   existing readers/cards work) + the full checklist sections + safety fields from the spec (`source_track`,
   `canonical_submission_ready_source`, `human_review_required`, `no_submit_controls`, `browser_computes_severity:false`,
   `l3_status`, `high_promotion_allowed`, `high_promotion_blocker`, `raw_fields`, …) + `schema:"synced-1"`.
2. **Adapter** `scripts/dashboard_sync.py` (pure, no I/O): `to_synced_finding(bundle) -> dict` maps any candidate
   bundle (candidate-register row, triage result, deep_trace, min_confirm, confirm_gate, `submission_readiness_review`
   overlay/`l3_evaluate`, L3 record, harness result, report-package path, dry-run-queue record, post-score notes,
   source_refs) → the canonical schema. Rules: missing → `"unknown"`/`"MISSING_EVIDENCE"`; **no inferred severity**
   (only echo recorded `severity_recommendation`/`claimed_severity`; else leave for `_sev_or_status`→HUMAN_PENDING);
   `submission_ready:false` always; `routing_allowed:false`; `research_only:true`/`routes_in_production:false`. A
   companion `to_funnel_record(synced)` emits the funnel-1-valid record (enum-clamped) that also carries the
   runtime-style field names `build_verifier_evidence` consumes (`surface_function`, `contract_function`/`target`,
   `suspected_mechanism`, `mechanism_correctness`, `severity_gate`, `severity_recommendation`/`claimed_severity`,
   `novelty_status`, `reachability_verdict`, `p155_gate1_source_intent`, `p155_gate2_attacker_model`,
   `vulnerable_output`, `limitations`, `artifact_links`) PLUS inline sections (`exploit_steps`, `attacker_model`,
   `defense_map`, `intent_scope_operator_assumptions`, `red_flags`, `function_map`).
3. **Generator** `scripts/build_synced_findings.py` (CLI): gather P215 sources from
   `p215_full_funnel_rehearsal/CANDIDATE_REGISTER.json` + `output_research/l3_readiness/ZETA-*.json` +
   `audits/zetachain-2023-10-holdout/data/triage/*` + `output_research/dry_run_submission_queue/*` +
   `ANSWER_KEY_SCORECARD.md` notes → adapter → write `synced_findings.generated.json`. **Backup before write,
   idempotent (key by `record_id`), schema-validate each record, no duplicates, reversible.**
4. **Reader merge (one additive change)** `scripts/funnel.py` `load_records()`: after reading `funnel_records.json`,
   also read `SYNCED_RECORDS_PATH = …/synced_findings.generated.json` and concat its `findings` into `raw_findings`
   before `normalize_record`. Guarded (missing file = no-op); tag passthrough `source_track`. Backward compatible.
5. **Renderer edit (minimal, additive, read-only)** `scripts/finding_detail.py` `build_verifier_evidence()`: where it
   currently derives `exploit_steps`/`defense_map`/`attacker`/`function_map`/intent/red-flags from markdown docs, prefer
   the record's **inline** synced fields when present (`raw.get("exploit_steps")`, `raw.get("defense_map")`,
   `raw.get("attacker_model")`, `raw.get("function_map")`, `raw.get("intent_scope_operator_assumptions")`,
   `raw.get("red_flags")`) before the doc fallback. **Never** touch severity (`_sev_or_status` unchanged) or
   routing/submission flags.
6. **Migration:** backup current `funnel_records.json`; restore it to the pre-P215 8-record backup
   (`funnel_records.json.bak.20260607T050647Z`); run the generator so the 12 ZETA candidates live only in the mirror.

## Files
- **New:** `scripts/dashboard_sync.py`, `scripts/build_synced_findings.py`,
  `documentation/research/funnel/synced_findings.generated.json` (output),
  `tests/research/test_dashboard_sync.py`, and `documentation/research/assisted_mode/p216_dashboard_sync_contract/`
  (all deliverables + `SYNCED_FINDING_SCHEMA.json`).
- **Edit (additive, reviewed):** `scripts/funnel.py` (`load_records` 2nd-file merge), `scripts/finding_detail.py`
  (`build_verifier_evidence` inline-section preference).
- **Migrate (data):** `documentation/research/funnel/funnel_records.json` → restored to pre-P215 (8 records).
- **Untouched:** `prompts/deep_trace.md`, `scripts/min_confirm_gate.py`, `scripts/confirm_gate.py`,
  `config/runtime_policy.json`, `scripts/dashboard.py` route handlers, all HTML/JS (no submit/promote controls added;
  browser never computes severity).

## Verification (read-only + tests; dashboard server flaky → call handlers directly)
1. Integrity precheck: START/END md5 for `dashboard.py`, `findings_overview.py`, `funnel.py`, `candidate_detail.py`,
   `finding_detail.py`, `submission_readiness_review.py`, `final_submission_pack.py`, `funnel_records.json`,
   `runtime_policy.json`, `output_research/option_a_campaign/ledger.jsonl`. Only `funnel.py`, `finding_detail.py`,
   `funnel_records.json` change; record before→after. `api_free=true` unchanged.
2. Run generator → `synced_findings.generated.json` valid; 12 records; backup created.
3. `funnel.load_records()` returns 8 (curated) + 12 (mirror); `findings_overview.load_overview()` lists 12 ZETA funnel
   rows; `dashboard.api_funnel()/api_findings()/api_candidates()` all render them; `routing_allowed:false`,
   `research_only:true`. **No active-audit switch required** (global funnel track).
4. `finding_detail.load_unified_detail("funnel:ZETA-04")` → `verifier_evidence` has all sections populated or
   `MISSING_EVIDENCE`; `severity_recommendation` is a severity/HUMAN_PENDING (never a conversion token);
   `submission_ready:false`, `routing_allowed:false`.
5. Idempotent re-run (byte-identical); schema-validate; safety flags false on every record.
6. `tests/research/test_dashboard_sync.py` green: schema validation · idempotence · no duplicates · safety flags always
   false · missing→unknown · P215 visible in all three readers · H5 parity structure · no submit/promote controls in
   HTML · no active-audit switch · zero route/submit side effects.
7. `FINISHED_BUG_PARITY.md`: one ZETA record vs H5 card — same sections + safety semantics (content may differ).

## Future routing rule (deliverable FUTURE_ROUTING_RULE.md)
Every candidate reaching {confirmed mechanism · needs harness · L3 PASS · L3 FAIL-for-High · dry-run-queue entry ·
human-reviewable Med/High · source-refuted important FP · post-score HIT/PARTIAL/ADJACENT/MISS} MUST be emitted through
`dashboard_sync.to_synced_finding` into the mirror. Unsynced only if: rejected as pure noise before candidate-id
assignment · duplicate scratch output · explicitly `scratch_only:true`.

## Deliverables
P216_PLAN.md · INTEGRITY_PRECHECK.md · CURRENT_DASHBOARD_DATA_FLOW.md · SYNCED_FINDING_SCHEMA.json ·
DASHBOARD_SYNC_CONTRACT.md · WRITER_DESIGN.md · P215_BACKFILL_RESULTS.md · FINISHED_BUG_PARITY.md ·
DASHBOARD_VERIFICATION.md · FUTURE_ROUTING_RULE.md · TEST_RESULTS.md · P216_RECOMMENDATION.md · metrics.json ·
integrity_checks.md.

## Decision space
`DASHBOARD_SYNC_CONTRACT_READY` (12 ZETA visible in all three; future path defined; H5-structural parity; unknowns
explicit; L3/blockers visible; no submit/promote; routing_allowed/submission_ready false; browser no severity;
idempotent+reversible; hashes recorded; JSON valid) · `DASHBOARD_SYNC_PARTIAL` · `DASHBOARD_SYNC_FAILED_SAFETY_FLAGS` ·
`DASHBOARD_SYNC_FAILED_VISIBILITY` · `INVALID_RUN`. **Expected: READY.**
