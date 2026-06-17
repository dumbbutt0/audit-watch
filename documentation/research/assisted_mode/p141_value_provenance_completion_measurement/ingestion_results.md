# P141 — Ingestion Results

Per-architecture `run_value_provenance_advisories.py --ingest-results` (the unchanged P140 loop). Raw ingestion
reports saved as `{noya,blackhole,size}_ingestion.json`.

| Arch | queued | accepted | rejected/quarantined | unmatched | completed | pending after |
|---|---|---|---|---|---|---|
| noya | 2 | 2 | 0 | 0 | 2 | 0 |
| blackhole | 3 | 3 | 0 | 0 | 3 | 0 |
| size | 2 | 2 | 0 | 0 | 2 | 0 |
| **TOTAL** | **7** | **7** | **0** | **0** | **7** | **0** |

## Notes
- Match key `job_id == advisory_id` resolved cleanly for all 7 (0 unmatched).
- 0 quarantined — every artifact passed the safety validator (no unsafe/forbidden fields, valid decision/
  confidence/next-step).
- Noya jobs came from the real P139 trigger; blackhole/size jobs were `eval_only_manual_queue` (clearly tagged).
- Every merged entry retained `advisory_only=true / submission_ready=false / requires_human_review=true` (forced).
- Re-running ingestion is idempotent (verified in P140; field copy is deterministic).
