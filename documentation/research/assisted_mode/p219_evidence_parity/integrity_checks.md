# P219 — INTEGRITY CHECKS (END)

## Hashes START → END (md5 first-8)
CHANGED (intended): scripts/sync_hunt_findings.py `8d8a3203`→`87764e5e` (richer extraction + provenance) ·
scripts/finding_detail.py `f12aa8d3`→`78c41bf5` (additive inline impact preference) ·
synced_findings.generated.json `d578cd87`→`c7166e71` (richer; same 12 ids).
SAME (byte-identical): dashboard_sync.py `26bd7ee0` · validate_hunt_sync_completion.py `00cf5f56` ·
run_hunt_sync_hook.py `9e38136e` · funnel.py `d9f09981` · findings_overview.py `5c6cccb5` · dashboard.py `197ac4d5` ·
submission_readiness_review.py `e4960878` · funnel_records.json `b3278eed` · runtime_policy.json `bea43487` ·
ledger `e23c5bc9` · deep_trace.md `ef93a6c2` · min_confirm_gate.py `41dd3c96` · confirm_gate.py `4fadfc5f`.

**dashboard_sync.py NOT edited** (card fields injected in the wrapper). Forbidden files untouched. run_pipeline.sh not touched.

## Safety
- HARD RULE: a field is populated only if it ties to a specific artifact path (`_field_provenance`); else unknown/
  MISSING_EVIDENCE. No invented evidence.
- Post-score answer-key notes only in `scoring_note`/`last_reviewer_note`; no blind-evidence field sourced from the
  scorecard; `conversion` stays an enum.
- NEEDS_HARNESS candidates keep executed-PoC fields explicitly absent.
- Severity recorded-or-HUMAN_PENDING; `submission_ready`/`routing_allowed` false; `browser_computes_severity` false;
  `high_promotion_allowed` from server-side `decide()`. No submit/promote controls.
- Hook exit 0; completion guard PASS; idempotent (byte-identical re-run); mirror backups retained (reversible).

## Tests / JSON
test_evidence_extraction.py 12/12; full regression — see TEST_RESULTS. metrics + mirror JSON valid; fabrication 0.
