# P218 — SYNC COMPLETION VALIDATION

## Checks (FAIL = hard; WARN = soft, fatal under --strict; NOTE = informational)
1. every register candidate has a synced record — **FAIL**
2. no stale phase/audit synced record absent from the register (unless `--allow-extra`) — **FAIL**
3. every synced record `dashboard_sync.validate_synced(rec)==[]` — **FAIL**
4. every record passes the 9 safety flags (`_safety_ok`) — **FAIL**
5. `final_triager_decision` present (triage status or explicit no-triage reason) — **FAIL**
6. High/Critical: `high_promotion_allowed` not True unless `l3_status ∈ {PASS,HUMAN_OVERRIDE}`; if blocked, a
   `high_promotion_blocker` must be recorded — **FAIL**
7. readers see each record (`funnel.load_records`, `findings_overview.load_overview`) — **FAIL**
8. detail card loads with 15 verifier sections + safe flags — **FAIL**
9. **every dry-run-queue id has a synced record** (reviewer-added) — **FAIL**
10. no duplicate `record_id`s — **FAIL**
11. queued candidate has a package/queue link in `source_refs` — **WARN**
12. sync metrics file present — **NOTE**

## Example — SUCCESS (real P215 mirror)
```json
{ "phase":"P215","audit":"zetachain-2023-10-holdout","register_candidates":12,"synced_records":12,
  "synced_unique_candidates":12,"dry_run_queue_ids":["ZETA-04","ZETA-07","ZETA-12"],
  "duplicate_record_ids":[],"failures":[],"warnings":[],"ok":true,"research_only":true,"routes_in_production":false }
```
Exit 0. (Full hook run: reader_failures=[], card_failures=[].)

## Example — FAILURE (ZETA-04 missing from the mirror)
```json
{ "register_candidates":12,"synced_records":11,"synced_unique_candidates":11,
  "dry_run_queue_ids":["ZETA-04","ZETA-07","ZETA-12"],
  "failures":[ "ZETA-04: missing from synced mirror",
               "dry-run-queue entry ZETA-04 has no synced dashboard record" ],
  "ok":false }
```
Exit 1 — the missing candidate trips both check 1 and the reviewer-added dry-run-queue check.
