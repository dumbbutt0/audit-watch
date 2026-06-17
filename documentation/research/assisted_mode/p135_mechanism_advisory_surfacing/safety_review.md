# P135 — Safety Review

All checks pass (measured on the noya prod-default and eval outputs).

| Safety property | Result |
|---|---|
| Advisory entries cannot become submission packages | ✅ separate artifact `output/mechanism_advisory_context.json` carries `routing_allowed:false`, `submission_ready:false`; queue entries `finding_id:null`, `advisory_only:true` |
| Submission gates unchanged (still require human/PoC/impact) | ✅ no submission/min_confirm/confirm_gate logic touched |
| research_only status preserved | ✅ STC/RPL entries carry `detector_status:research_only`; surfaced only with `surface_research_only_advisories` |
| report_only status preserved | ✅ units entries carry `detector_status:report_only`, `submission_ready:false` |
| No severity assigned from advisory evidence | ✅ no `severity` field on any entry (verified: 0/all) |
| No platform/submit path touched | ✅ no submission/ code changed |
| Review wording doesn't overstate confidence | ✅ confidence copied verbatim; `forbidden_next_steps` includes `mark_confirmed_without_poc_or_human_review`; review_gate not altered (advisory kept in a separate artifact) |
| Existing human-review gate remains mandatory | ✅ every entry `requires_human_review:true`; nothing auto-clears |
| Disable switches present | ✅ master `surface_mechanism_advisories:false` → 0 surfaced (verified); per-status + per-detector + caps |
| Unsafe entries (submission_ready / not advisory_only / not requires_human_review / has severity) | ✅ **0** in both prod and eval |
| P130–P134 behavior preserved | ✅ no detector/severity/submission/gate logic changed; only a new script + config block + tests |

## Residual safety notes
- The eval-mode standalone queue append writes to the audit-local `human_review_queue.jsonl` as **review_context**
  (advisory_only, finding_id:null) — it cannot be mistaken for a triaged finding by the human-queue consumer
  (distinct `advisory_id`, no severity/score). Restored to the P133 baseline after measurement.
- Default production posture is conservative: advisory+report surfaced (covers all 3 P133 MISS), research-only
  **off**, standalone queue **off** — so a production run gains the recall-reaching-review benefit without
  research-only noise or queue growth unless explicitly enabled.
