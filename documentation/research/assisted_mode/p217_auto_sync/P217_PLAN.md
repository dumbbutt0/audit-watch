# P217 — Automate synced-finding emission + programmatic field population

## Context
P216 shipped the dashboard sync contract (`dashboard_sync.to_synced_finding`, the `synced_findings.generated.json`
mirror, the `funnel.load_records` merge, the `finding_detail` full-record card). But it still requires running a
generator by hand, and many synced fields stay `unknown`/`MISSING_EVIDENCE` even though the P215 artifacts contain the
information (exploit steps, attacker model, defense/fix, mechanism, root cause, post-score verdicts). P217 adds the
**automation layer**: a generic per-hunt wrapper that extracts those fields from the real artifacts and emits richer
synced records — proven by re-syncing the 12 P215 ZetaChain candidates with measurably higher field completeness, while
preserving every safety semantic.

Recon — the richer sources already exist (verified):
- `audits/zetachain-2023-10-holdout/output/merged_findings.json`: `description` (one-sentence mechanism),
  `ice_chain.exploit_path` (exploit steps), `ice_chain.impact`/`impact`, `ite.{intent,technique,evasion}`,
  `location.{file,lines,function}`, `_attacker_model`, `_impact_class`, `manifest_refs`, `proof_of_concept`.
- `…/data/triage/<bucket>.jsonl`: `decision_reason` (final triager rationale), `follow_up_packet` (the fix → defense
  map), `ice`, `recommended_severity`, `triage_status`.
- `output_research/l3_readiness/ZETA-*.json`: `l3_status`, `expected_delta_or_control`, `source_validity_notes`,
  `poc_path/command/result`, `affected_asset_or_state`; `decide()` (flag-on) → calibrated/blocker/high_allowed.
- `output_research/dry_run_submission_queue/ZETA-*.json`: `readiness_state`.
- `…/p215_full_funnel_rehearsal/{ANSWER_KEY_SCORECARD,FINDING_MATCHES,SEVERITY_CALIBRATION}.md`: per-id post-score
  verdicts (HIT/PARTIAL/ADJACENT/MISS/SEVERITY_UNDER/TRUE_NEGATIVE) — parsed by id mention.
- `CANDIDATE_REGISTER.json`: id/contract/function/file/lines/threat_ceiling/claimed_severity/impact_class/
  **attacker_model**/title.

Key fact: `dashboard_sync.to_synced_finding` already accepts and passes through `exploit_steps`, `attacker_model`,
`defense_map`, `function_map`, `red_flags`, `root_cause`, `intent_scope_operator_assumptions`, etc., and
`finding_detail.build_verifier_evidence` already prefers inline sections (P216). **So the completeness gain comes purely
from feeding richer bundles — no change to `dashboard_sync.py`/`funnel.py`/`finding_detail.py` is required.**

## Approach
1. **New generic wrapper** `scripts/sync_hunt_findings.py` — the automation layer, not P215-hardcoded. CLI:
   `--phase --audit --workspace --candidate-register --l3-dir --dry-run-queue --scorecard --out`
   + modes `--dry-run` (print, write nothing) / `--write` / `--strict` (fail on any safety/validation error) /
   `--replace-phase-records` (drop stale records sharing this phase/audit prefix). It:
   - discovers candidate ids from the register;
   - auto-resolves audit-internal artifacts from `--audit` (`output/merged_findings.json`, `data/triage/*`);
   - per candidate loads register + merged finding + triage record + L3 record (+ `decide()` flag-on) + dry-run-queue
     record + harness (from L3 `poc_path`/`pocs/`) + scorecard verdict (parsed by id);
   - builds a rich bundle (see Field-population map) and calls `dashboard_sync.to_synced_finding` + `validate_synced`;
   - **completeness-scores** each record; backs up the mirror before write; upserts by `record_id` (idempotent);
     never writes route/submit output.
   - Prints: records emitted / updated / unchanged / missing-artifact warnings / field-completeness / safety result /
     mirror path.
2. **Field-population map** (`FIELD_POPULATION_MAP.md`): the table above, source→synced field, with "leave
   unknown/MISSING_EVIDENCE if absent; never invent."
3. **Completeness scorer** (in the wrapper): per record — expected checklist fields, populated, `unknown`,
   `MISSING_EVIDENCE`, artifact-backed, safety-valid, percentage. **Safety defaults do NOT count toward evidence
   completeness.** Computed BEFORE (current P216 mirror, snapshot first) and AFTER (P217).
4. **Retire the P216 P215-only generator**: refactor `scripts/build_synced_findings.py` into a thin shim that calls
   `sync_hunt_findings` with the P215 args (single source of truth; prevents a stale lower-fidelity generator from
   downgrading the mirror).
5. **Re-sync P215**: run `--dry-run` then `--write` to regenerate all 12 ZETA records (same `record_id`s) with the
   richer fields.

## Files
- **New:** `scripts/sync_hunt_findings.py`; `tests/research/test_sync_hunt_findings.py`;
  `documentation/research/assisted_mode/p217_auto_sync/` (all deliverables).
- **Edit:** `scripts/build_synced_findings.py` → thin shim (single source of truth).
- **Regenerated (data):** `documentation/research/funnel/synced_findings.generated.json` (richer; same 12 ids).
- **Unchanged (verify byte-identical):** `scripts/dashboard_sync.py`, `scripts/funnel.py`, `scripts/finding_detail.py`,
  `scripts/findings_overview.py`, `scripts/dashboard.py`, `scripts/submission_readiness_review.py`,
  `scripts/final_submission_pack.py`, `documentation/research/funnel/funnel_records.json`, `config/runtime_policy.json`,
  `output_research/option_a_campaign/ledger.jsonl`, and the forbidden `deep_trace.md`/`min_confirm_gate.py`/
  `confirm_gate.py`.

## Field-population map (source → synced field)
title←register.title · summary←merged.impact/description · affected_contracts/functions←register/merged.location ·
mechanism←merged.description · root_cause←merged.ite.intent / l3.source_validity_notes · attacker_model←register.attacker_model ·
exploit_steps←merged.ice_chain.exploit_path (split) · function_map←register contract.function + impact_class role ·
defense_map←triage.follow_up_packet / l3.expected_delta_or_control (the recommended fix = the missing defense) ·
poc_verification←l3.poc_path/command/result + harness (ZETA-07) + merged.proof_of_concept ·
impact_and_severity←merged.impact + triage.recommended_severity + l3 calibrated + register.claimed_severity ·
intent_scope_operator←register.attacker_model (privileged⇒operator dep) + triage.decision_reason ·
novelty_duplicate←unknown (no data) · conversion_classification←scorecard verdict · main_blocker←decide().blocker ·
final_triager_decision←triage.triage_status + decision_reason · red_flags←derived from attacker_model + l3 (no control/needs_harness) ·
evidence_backup←source_refs+harness+l3+scorecard · l3_status/high_promotion_allowed/blocker←decide() (flag-on) ·
dry_run_queue←drq.readiness_state · post_score note←scorecard. **No invention; absent ⇒ unknown/MISSING_EVIDENCE.**

## Verification
1. Integrity: START/END md5 of the files above; only the mirror + `build_synced_findings.py` (shim) change among
   tracked files. `api_free=true`.
2. `--dry-run` writes nothing (mirror hash unchanged); `--write` emits 12, 0 duplicates, same ids as P216.
3. Completeness AFTER > BEFORE (per-field improvement table; safety defaults excluded).
4. Safety: all 12 satisfy the 9 flags or the run fails (`--strict`).
5. Detail cards `funnel:ZETA-04/07/11` → 15/15 sections, now with populated mechanism/exploit_steps/defense_map/
   attacker_model; severity recorded-or-HUMAN_PENDING (never a conversion token); `submission_ready/routing_allowed:false`.
6. Readers/API: `funnel.load_records()`, `findings_overview.load_overview()`, `api_funnel/api_findings/api_candidates`
   include the 12; no active-audit switch.
7. Idempotent: re-run `--write` → byte-identical mirror. Reversible: `--replace-phase-records` with empty input (or
   delete the phase records / restore backup) → pre-P217 state.
8. Tests: new `test_sync_hunt_findings.py` (dry-run writes nothing · write emits · idempotence · safety · completeness
   scoring · readers visibility · detail sections · unknowns explicit · zero route/submit · no audit switch) +
   P216 regression suite still green.

## Deliverables
P217_PLAN.md · INTEGRITY_PRECHECK.md · AUTO_SYNC_DESIGN.md · IMPLEMENTATION_NOTES.md · FIELD_POPULATION_MAP.md ·
COMPLETENESS_SCORECARD.md · P215_RESYNC_RESULTS.md · DASHBOARD_VERIFICATION.md · IDEMPOTENCE_AND_REVERSIBILITY.md ·
TEST_RESULTS.md · P217_RECOMMENDATION.md · metrics.json · integrity_checks.md.

## Decision space
`AUTO_SYNC_READY` (wrapper exists + generic; 12 ZETA re-synced from real artifacts; completeness improved over P216; no
invented fields; unknowns explicit; all safety flags enforced; visible in all 3 pages; cards 15/15; idempotent +
reversible; hashes recorded; JSON valid) · `AUTO_SYNC_PARTIAL_FIELD_GAPS` · `AUTO_SYNC_FAILED_SAFETY_FLAGS` ·
`AUTO_SYNC_FAILED_VISIBILITY` · `AUTO_SYNC_FAILED_IDEMPOTENCE` · `INVALID_RUN`. **Expected: AUTO_SYNC_READY.**
