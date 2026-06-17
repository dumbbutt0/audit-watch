# P218 — REQUIRED WRITE CONTRACT

A hunt/rehearsal/eval is **complete only if** every candidate id satisfies all of the following; missing data must be
an explicit token (`unknown` / `MISSING_EVIDENCE` / `NOT_ATTEMPTED` / `NEEDS_HARNESS` / `BLOCKED`) — never silently
omitted. Enforced by `scripts/validate_hunt_sync_completion.py`.

| # | Requirement | Guard check | Severity |
|---|-------------|-------------|----------|
| 1 | Candidate appears in the candidate register | register is the denominator | — |
| 2 | Candidate appears in the synced mirror | check 1 | **FAIL** if missing |
| 3 | Candidate has triage status or explicit no-triage reason | `final_triager_decision` populated/explicit | FAIL if blank |
| 4 | Candidate has confirm status or explicit no-confirm reason | record present + readers see it | FAIL |
| 5 | High/Critical has L3 record OR explicit missing-L3 blocker | check 7: High blocked unless L3 PASS/override | **FAIL** |
| 6 | Reportable/queued candidate has package or explicit blocker | check 8/9: queued ⇒ synced + package ref | **FAIL** (queued w/o sync) / WARN (no pkg link) |
| 7 | Candidate appears in synced mirror & schema-valid | `validate_synced==[]` | **FAIL** |
| 8 | Dashboard detail card loads | `load_unified_detail` → 15 sections | **FAIL** |
| 9 | Safety flags present & safe | `safety_ok` (9 flags) | **FAIL** |
| 10 | No extra stale phase/audit synced records absent from register | check 2 | FAIL (unless `--allow-extra`) |
| 11 | No duplicate `record_id`s in the mirror | dedup check | **FAIL** |
| 12 | **Dry-run queue entry ⇒ synced dashboard record** (added per reviewer) | check 8 | **FAIL** |

Missing-field tokens are display-only and never flip `submission_ready`/`routing_allowed`; severity is recorded or
`HUMAN_PENDING` (never browser-computed).
