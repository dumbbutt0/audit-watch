# P211 — End-to-end rehearsal with AUDITWATCH_L3_READINESS=1 (known corpus, no live hunt)

## Context
P210 dark-wired the L3 HIGH readiness gate behind default-off `AUDITWATCH_L3_READINESS` (only `submission_readiness_review.py`
+ a read-only `dashboard.py` panel changed; flag-off output-equivalent; flag-on blocks High-without-L3). P211
rehearses the full workflow with the flag ON on a known/old corpus, verifying the wired path end-to-end with no
submit/route/promote side effects and human review still mandatory. Not a live hunt.

## Recon (read-only) — decides the rehearsal shape
- Active audit = **quantamm-2024-12-eval** (a BLIND eval in progress, 4 submit candidates). Do NOT disturb or score it.
- **decent-2024-01-holdout has its sealed answer key but NO `output/` pipeline artifacts** (no merged_findings/triage/
  confirm) → a literal discovery replay isn't available and is out of scope for a rehearsal.
- The L3 wiring reads `ROOT/output_research/l3_readiness/<candidate_id>.json` (ROOT-relative, audit-independent) and
  enforces via `submission_readiness_review.evaluate()`/`l3_evaluate()`/`detail_overlay()`/`record_review()`; dashboard
  computes its panel via the same `l3_evaluate()`. So the L3-relevant surface can be rehearsed end-to-end by driving
  the REAL wired functions with decent candidate fixtures + real L3 records — without switching the active audit.
- L3 evidence already exists and is reusable: P204 (decent H-01 setRouter→mint PASS; M-03 receiveFromBridge demoted)
  and P207 (vultisig H-01 PASS; M-03 demoted), with executed forge harnesses. No new harness needed.

## Approach: faithful wired-path rehearsal on decent (self-contained, active audit untouched)
Corpus = **decent-2024-01-holdout** (answer key present; P204 L3 evidence; light deps; no live risk). Rehearse the
L3 touchpoints (readiness → dashboard → package) through the production functions, flag-off vs flag-on, then score vs
the decent answer key. A small read-only rehearsal driver under `p211_e2e_rehearsal/` calls the real functions (it does
not reimplement them); for `record_review` it monkeypatches `_unified_keys` to admit the rehearsal ids so the full
append-only write path is exercised (proving it flips no canonical flags).

## Strict scope
No live target; no submit; no route-to-submit; no auto-promote/demote; no `deep_trace.md`/`min_confirm_gate.py`/
`confirm_gate.py`/canonical-label/answer-key change; human review mandatory; L3 blocks High readiness only, never
discovery. Production stays byte-identical except the two P210 files. The active quantamm audit is not switched or
scored.

## Execution sequence (deliverables under `documentation/research/assisted_mode/p211_e2e_rehearsal/`)
1. **INTEGRITY_PRECHECK.md** — START hashes: `deep_trace.md ef93a6c2`, `min_confirm_gate.py 41dd3c96`,
   `confirm_gate.py 4fadfc5f`, `submission_readiness_review.py 7c4b563d`, `dashboard.py 857d593a`,
   `final_submission_pack.py 57cba16d`, `validate_p208_l3_readiness.py 7e148e18`, ledger `fc446040`,
   `config/runtime_policy.json`. Confirm `api_free=true`, no live route, flag OFF by default; note flag is enabled only
   for the P211 process (env), never persisted to config.
2. **TARGET_SELECTION.md** — decent: source+answer-key availability, light deps, known High/Medium mix (awarded H-01..,
   M-01..), P204 PoC feasibility (already executed), no live submission risk; note the no-`output/` constraint → wired-
   surface rehearsal.
3. **FLAG_OFF_BASELINE.md** — with flag unset, run the driver over decent candidate fixtures (H-01 High, M-03 Medium,
   a static-High-no-PoC): record `evaluate()`/`detail_overlay()` outputs → no `l3` fields, no `blocked_by_missing_l3_poc`;
   dashboard build path attaches no `l3` key. Confirms pre-P210 equivalence.
4. **FLAG_ON_REHEARSAL.md** — with `AUDITWATCH_L3_READINESS=1`: same candidates → High+PASS clears, High-without-L3 →
   `blocked_by_missing_l3_poc`, Medium unaffected, dashboard `l3` panel present + read-only; record no route/submit
   side effects.
5. **L3_EVIDENCE_RECORDS.md** + place records at `output_research/l3_readiness/`: decent-H-01 (PASS, from P204), decent-
   M-03 (FAIL/demoted, from P204) [+ optionally vultisig H-01 PASS]. Each cites poc_path/command/result + actual vs
   control delta. (Reuse; no new harness — `pocs/p211/` only if anything new, else a pointer to P204/P207.)
6. **SUBMISSION_READINESS_RESULTS.md** — run the 6 cases through the real functions (monkeypatch `_unified_keys` for the
   write path): High no-record→block; High PASS→clears (other human checks still apply); Medium no-L3→unaffected;
   malformed High→fail-closed; human-override+reason→allowed+visible+no auto-submit; override-no-reason→blocked. Assert
   every returned row carries `routing_allowed:false` and never `submission_ready:true`.
7. **DASHBOARD_SMOKE_TEST.md** — exercise the dashboard L3 computation (`l3_evaluate` + the P210 attach guard) flag
   on/off: panel only when on, read-only, blocker + poc_path/command visible, Medium unaffected, no submit/promote
   controls.
8. **FINAL_PACKAGE_REHEARSAL.md** — assemble an "equivalent" report package for the decent H-01 candidate combining
   `final_submission_pack`'s existing fields (affected fns/attacker/exploit steps/source refs/impact/mitigation/
   assumptions/human note) + the L3 overlay fields (l3_status/poc_path/poc_command/actual/expected-control). Verify it
   carries L3 evidence and shows NO auto-submit. (final_submission_pack.py NOT modified — hash unchanged; wiring L3 into
   it is a noted follow-up.)
9. **ANSWER_KEY_SCORECARD.md** — vs decent `_sealed_answer_key` (read-only): H-01 awarded High + L3 PASS → cleared
   (correct preserve); M-03 awarded Medium / blind-rated High → blocked from High (correct demote); record hits/
   partials/FPs, severity correctness, L3-blocker correctness, package completeness.
10. **FAILURE_CASES.md** + **metrics.json** (candidates, High-ceiling count, Highs blocked-for-missing-L3, Highs
    allowed-by-PASS, Mediums unaffected, malformed blocked, dashboard mismatches=0, package completeness, route/submit
    side effects=0, flag-off↔flag-on diff) + **P211_RECOMMENDATION.md** + **integrity_checks.md** (END==START) + copy
    plan → **P211_PLAN.md** + memory.

## Decision space
`E2E_REHEARSAL_READY_FOR_REAL_HUNT` (flag-off clean; High-without-L3 blocked; High+PASS clears; Medium unaffected;
dashboard read-only; package carries L3; 0 route/submit side effects; answer-key scoring recorded; hashes byte-identical
START==END) · `E2E_REHEARSAL_PARTIAL` · `E2E_REHEARSAL_FAILED_L3_REGRESSION` · `E2E_REHEARSAL_FAILED_PACKAGE_READINESS`
· `E2E_REHEARSAL_FAILED_SIDE_EFFECT_GUARD` · `INVALID_RUN`. **Expected:** `READY_FOR_REAL_HUNT`.

## Acceptance criteria
Known/old corpus (decent), not live; flag tested end-to-end; flag-off baseline clean; High-without-L3 blocked; High+
PASS clears; Medium unaffected; dashboard L3 read-only; package includes L3 evidence; no route/submit/promote side
effects; answer-key scoring recorded; production hashes byte-identical START==END (the two P210 files at their P210
END hashes `7c4b563d`/`857d593a`, all other gates/prompt/ledger unchanged); `api_free=true` unchanged; JSON valid;
flag never persisted to config.

## Verification
Driver run flag-off → no `l3`/blocker (matches pre-P210); flag-on → decent H-01 clears, M-03 + static-High blocked,
Medium untouched; `record_review` rows show `routing_allowed:false`, no `submission_ready:true`; dashboard panel only
flag-on + read-only; package doc contains all required fields incl L3; `metrics.json` valid; hashes unchanged at END;
active audit still quantamm (not switched).

## Follow-on (NOT this phase)
Enable the flag on a real hunt + wire L3 fields into `final_submission_pack.py` rendering + cost model for L2/L3 harness
authoring (auto-scaffold vs human). Deep-pass recall + oracle track remain separate.
