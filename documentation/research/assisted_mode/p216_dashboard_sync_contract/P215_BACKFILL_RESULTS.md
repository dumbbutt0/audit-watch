# P216 — P215 BACKFILL RESULTS

All 12 P215 ZetaChain candidates re-emitted through `dashboard_sync.to_synced_finding` into
`documentation/research/funnel/synced_findings.generated.json` (schema `synced-1`). `funnel_records.json` restored to
its pre-P215 8 curated records (migration). No duplicates; idempotent re-run byte-identical.

| ZETA | source_track | conversion | severity (recorded) | l3_status | main_blocker | dry-run | post-score note |
|------|--------------|-----------|---------------------|-----------|--------------|---------|-----------------|
| 01 | audit_workspace | NONE | Medium | NEEDS_HARNESS | blocked_by_missing_l3_poc | — | no official match |
| 02 | audit_workspace | ADJACENT | Low | NOT_ATTEMPTED | — | — | ~ QA[05] |
| 03 | audit_workspace | ADJACENT | Low | NOT_ATTEMPTED | blocked_by_missing_l3_poc | — | HIT == QA[09] (Low) |
| 04 | audit_workspace | CLEAN_HIT | Medium | NEEDS_HARNESS | blocked_by_missing_l3_poc | pending-poc | **HIT == H-13 (High); UNDER** |
| 05 | audit_workspace | NONE | Medium | NEEDS_HARNESS | blocked_by_missing_l3_poc | — | no match (privileged) |
| 06 | audit_workspace | NONE | Medium | NEEDS_HARNESS | blocked_by_missing_l3_poc | — | no match |
| 07 | audit_workspace | ADJACENT | Low | PASS (executed) | — | ready (PoC) | non-awarded QA; harness 2/2 |
| 08 | audit_workspace | NONE | Low | NOT_ATTEMPTED | blocked_by_missing_l3_poc | — | centralization/QA |
| 09 | audit_workspace | REJECTED | Low | NOT_ATTEMPTED | rejected: by-design | — | TRUE_NEGATIVE |
| 10 | audit_workspace | NONE | High | NEEDS_HARNESS | blocked_by_missing_l3_poc | — | refuted theft claim |
| 11 | audit_workspace | STRONG_PARTIAL | Medium | NEEDS_HARNESS | blocked_by_missing_l3_poc | — | **PARTIAL ~ H-10 (High); UNDER** |
| 12 | audit_workspace | NONE | Medium | NOT_ATTEMPTED | — | pending-poc | non-awarded MEV/QA |

(Severity = the RECORDED triage recommendation, surfaced by the card; never inferred. L3 status from the L3 record;
blocker from the flag-on `decide()` verdict for High/Critical.)

## Visibility (verified by calling the readers directly; no active-audit switch)
- `funnel.load_records()` → 8 curated + 12 P215 = 20.
- `findings_overview.load_overview()` → 12 ZETA funnel rows.
- `dashboard.api_funnel()/api_findings()/api_candidates()` → 12 each; `routing_allowed:false`, `research_only:true`.
- `finding_detail.load_unified_detail("funnel:ZETA-xx")` → 15/15 verifier sections; severity recorded/HUMAN_PENDING;
  `submission_ready:false`, `routing_allowed:false`, `read_only_synced:true` for all 12.

## Safety
0/12 records violate any safety flag; `poc.human_submission_ready:false`; `submission.submission_status:NOT_STARTED`;
nothing routes/submits/promotes.
