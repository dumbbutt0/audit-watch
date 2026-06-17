# P140 — Safety Review

## Hard constraints (15) — all honored
1. No non-interactive LLM runner created. ✓ (loop ingests human-produced artifacts; execution stays in-session)
2. No external APIs. ✓
3. No new detector. ✓
4. No detector-logic change. ✓
5. No severity-logic change. ✓ (ingestion never assigns severity; bare `final_severity` is quarantined)
6. No submission-logic change. ✓
7. No gate pass/fail change. ✓ (all pipeline calls `|| true`; rendering never enters `findings`)
8. No auto-confirm. ✓ (`auto_run_status` only ever `completed`/`failed`; never "confirmed")
9. Nothing prompt-derived made submission-ready. ✓
10. Every completed result keeps `advisory_only=true / submission_ready=false / requires_human_review=true`. ✓
    (FORCED on merge regardless of artifact contents)
11. Human review + PoC still mandatory before severity/submission. ✓ (disclaimer + `requires_human_review`)
12. Ingestion deterministic + local. ✓ (file copy keyed on artifact; no network; idempotent)
13. Missing/malformed/manual artifacts never block. ✓ (fail-open `main()`; per-file quarantine; missing dir → [])
14. P130–P139 preserved. ✓ (all prior tests green; P139 build path unchanged)
15. Active audit restored to prior state. ✓ (symlink → quantamm-2024-12-eval; noya state restored)

## Defense-in-depth checklist
- **Quarantine gate** rejects `submission_ready:true`, `advisory_only:false`, `requires_human_review:false`,
  `confirmed:true`, bare `final_severity`, invalid decision/confidence/next-step, missing `job_id`.
- **Forced triplet** on every accepted merge — even a (hypothetical) artifact that passed validation but tried to
  carry unsafe values cannot flip the merged entry; the safe triplet is written unconditionally.
- **Isolation** — completed entries live only in `value_provenance_advisory_results.json`; the review-gate renders
  them in a separate advisory subsection and **never** adds them to `findings`, so Validated Findings and the
  confirmed-findings count are mathematically unaffected (verified: noya confirmed count 0 with a completed
  finding present).
- **No fabrication** — `SolvencyV2` left pending; the `NoyaValueOracle` completion is a real P137 in-session
  result, clearly attributed, with no answer-key issue IDs.

## Reversibility
`auto_run_value_provenance_advisories:false` (or `mode:off`) disables build + ingestion + rendering. The
`--ingest-results` pipeline calls are `|| true`; removing the manual-results dir reverts to pure-pending state.

## Residual risk
None that promotes prompt output. The only operator-facing risk is mislabeling a manual artifact, which the
quarantine gate catches; an accepted finding is still explicitly "NOT confirmed" and gated behind human + PoC.
