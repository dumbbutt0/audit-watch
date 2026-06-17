# P219 — Evidence parity: deepen Zeta /candidates cards to H5 evidence-source parity

## Context
P216–P218 made the 12 Zeta candidates visible in `/findings`,`/candidates`,`/funnel`, automated + enforced syncing,
and reached 90% field completeness. But several Zeta card sections are still shallow: attacker model is a generic
"conditional" sentence with no reachability verdict; PoC verification has no actual/expected/control/value-delta;
impact lacks who-loses/who-gains; red flags are thin; evidence_backup omits some pipeline artifacts. P219 deepens the
extraction so `/candidates` cards reach the Abracadabra H5 card's **evidence-source parity** (same kinds of evidence
points for human analysis) — from existing artifacts, **no invention**, unknowns explicit. Not about making Zeta
reportable or matching H5 content/severity.

Recon — the data already exists:
- **L3 records** (`output_research/l3_readiness/ZETA-*.json`): `affected_asset_or_state`, `actual_delta`,
  `victim_or_protocol_loss` (who-loses), `magnitude_basis` (value-delta), `expected_delta_or_control` (control),
  `poc_result`, `source_validity_notes`, `production_source_modified`, `poc_tier`. Rich for executed ZETA-07; honestly
  empty for NEEDS_HARNESS ZETA-04 (→ MISSING_EVIDENCE/NEEDS_HARNESS, not invented).
- **confirm/reachability_analysis.json**: per-candidate `reachability_status` / `suggested_action` / `blockers`.
- **merged_findings.json**: `description`, `ice_chain.exploit_path`, `ite`, `proof_of_concept`, `recommendation`.
- **report package** `audits/zetachain-2023-10-holdout/output/submission_pack.md`: per-finding Description / Proof of
  Concept / Recommendation / Location sections (fallback source).
- **Card render facts:** `finding_detail.build_verifier_evidence` PoC section already reads `raw.get("vulnerable_output"
  /corrected_output/control_case/runtime_delta)`; attacker `reachability_verdict` reads `raw.get("reachability_verdict")`
  — so those fill in from wrapper-injected record fields **with no renderer change**. BUT `who_loses`/`who_gains` are
  computed by a text heuristic (matches "honest staker"/"locker earns") that won't match Zeta → needs a tiny additive
  inline-preference edit (like P216).

## Approach (2 additive, read-only edits; dashboard_sync.py UNCHANGED)
1. **`scripts/sync_hunt_findings.py` — richer extraction adapters** (pure, the main work). After
   `to_synced_finding(bundle)`, inject the card-consumed top-level fields (so no `dashboard_sync.py` change needed):
   - **attacker reachability** ← `confirm/reachability_analysis.json[cid].reachability_status` (+ register
     attacker_model) → `reachability_verdict`.
   - **PoC actual/expected/control/delta** ← L3 record: `vulnerable_output`←actual_delta/poc_result,
     `control_case`+`corrected_output`←expected_delta_or_control, `runtime_delta`←magnitude_basis,
     `corrected_reference_type`←dependency_mocks. (Executed ZETA-07 → full; NEEDS_HARNESS → left empty/NEEDS_HARNESS.)
   - **impact** ← `who_loses`←victim_or_protocol_loss, `asset_or_value`←affected_asset_or_state,
     `loss_type`←impact_class mapping, `value/bounds`←magnitude_basis/source_validity_notes; `who_gains`←only if a
     beneficiary is stated, else `unknown` (most Zeta = DoS/availability/centralization → no gainer).
   - **red_flags** ← extend with L3-recorded facts (production_source_modified, control present, magnitude present,
     reachability) — derived, never guessed.
   - **evidence_backup / source_refs** ← add confirm-gate output, report package (`submission_pack.md`), merged_findings,
     harness — the full pipeline artifact set.
   - **report-package parse** ← fallback for `exploit_steps`/`impact`/`mitigation`/`assumptions` when merged is thin.
   - **provenance** ← `_field_provenance` map {field → source artifact} on the record (research-only, informational).
   - **post-score isolation** ← scorecard verdicts stay ONLY in `last_reviewer_note`/`scoring_note` (never feed blind
     fields); add a `blind_evidence:true` marker on non-scorecard fields' provenance.
2. **`scripts/finding_detail.py` — additive inline-preference** in `build_verifier_evidence`: prefer
   `raw.get("who_loses"/"who_gains"/"asset_or_value"/"loss_type")` over the text heuristic when present. Never touches
   severity (`_sev_or_status`), `submission_ready`, or `routing_allowed`.
3. **Regenerate** via `scripts/run_hunt_sync_hook.py --phase P215 --audit zetachain-2023-10-holdout --workspace …`
   (REPLAY_MODE — reuse frozen P215 candidates; only evidence-building re-run). Hook writes mirror + metrics, runs the
   P218 completion guard `--strict`.

## Files
- **Edit (additive, read-only):** `scripts/sync_hunt_findings.py`, `scripts/finding_detail.py`.
- **Regenerated (data):** `documentation/research/funnel/synced_findings.generated.json` (richer; same 12 ids),
  `output_research/funnel/sync_hook_metrics.json`.
- **New:** `tests/research/test_evidence_extraction.py`, `documentation/research/assisted_mode/p219_evidence_parity/`
  (14 deliverables).
- **Unchanged (verify byte-identical):** `scripts/dashboard_sync.py`, `scripts/funnel.py`,
  `scripts/findings_overview.py`, `scripts/dashboard.py`, `scripts/validate_hunt_sync_completion.py`,
  `scripts/run_hunt_sync_hook.py`, `scripts/build_synced_findings.py`, `run_pipeline.sh`, `funnel_records.json`,
  `runtime_policy.json`, ledger, and forbidden `deep_trace.md`/`min_confirm_gate.py`/`confirm_gate.py`.

## Verification
1. Integrity START/END md5; only `sync_hunt_findings.py`, `finding_detail.py`, the mirror + sync metrics change.
   `api_free=true`.
2. Hook re-run: exit 0, 12 records, no dups, safety preserved, completion guard PASS, idempotent (byte-identical re-run).
3. Completeness before(90%)→after (report per-candidate + per-section + unknown/MISSING/artifact-backed/human-only
   counts). No 100%-by-invention.
4. `/candidates` cards for all 12 load with 15/15 sections; ZETA-04/07/11 inspected: reachability verdict populated;
   ZETA-07 PoC actual/expected/control/delta populated (executed); who-loses/asset populated where L3 has it; remaining
   unknowns explicit. Severity recorded-or-HUMAN_PENDING; no submit/promote controls; no active-audit switch.
5. Post-score notes confirmed separate from blind evidence (`_field_provenance`).
6. Tests: new `test_evidence_extraction.py` (report-package/L3/harness extraction · red-flag derivation · post-score
   separation · idempotent · cards 15/15 · no unsafe · no invented evidence · completion guard passes) + full
   regression (P216/P217/P218 + funnel/overview/detail) green.

## Deliverables
P219_PLAN.md · INTEGRITY_PRECHECK.md · ABRACADABRA_H5_GOLD_STANDARD.md · ZETA_VS_H5_EVIDENCE_DIFF.md ·
ZETA_FIELD_SOURCE_MAP.md · EXTRACTION_IMPROVEMENTS.md · ZETA_RESYNC_RESULTS.md · CANDIDATES_PAGE_VERIFICATION.md ·
FIELD_COMPLETENESS_BEFORE_AFTER.md · H5_PARITY_RESULTS.md · TEST_RESULTS.md · P219_RECOMMENDATION.md · metrics.json ·
integrity_checks.md.

## Decision space
`H5_STYLE_DASHBOARD_PARITY_READY` (12 re-synced through the hook; `/candidates` shows all 12; ZETA-04/07/11 have
H5-style evidence sections suitable for human analysis; completeness improved or gaps explicitly justified; no invented
evidence; post-score separated; safety preserved; completion guard passes; hashes recorded; JSON valid) ·
`H5_STYLE_DASHBOARD_PARITY_PARTIAL` · `H5_STYLE_BLOCKED_BY_MISSING_ARTIFACTS` · `H5_STYLE_FAILED_VISIBILITY` ·
`H5_STYLE_FAILED_SAFETY` · `INVALID_RUN`. **Expected: H5_STYLE_DASHBOARD_PARITY_READY** (per-candidate: ZETA-07
READY incl PoC; ZETA-04/11 READY-for-analysis with explicit NEEDS_HARNESS; the 3 no-L3 candidates PARTIAL).
