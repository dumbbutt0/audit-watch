# P215 — DRY-RUN QUEUE AUDIT

Local queue: `output_research/dry_run_submission_queue/` (queue.jsonl + per-candidate + _manifest). **Submits nowhere.**
Every record: `external_submission:false`, `route_to_platform:false`, `submitted:false`, `human_review_required:true`,
`research_only:true`, `routes_in_production:false`.

## Entries (3) — gate: human-reviewable AND (High⇒L3 PASS/override) AND (Medium⇒source-proven)
| id | queued sev | readiness | L3 | post-scoring truth |
|----|-----------|-----------|-----|--------------------|
| ZETA-07 | Low | ready_for_submission_package (executed PoC) | PASS | non-awarded (admin-misconfig QA) — low, harmless |
| ZETA-04 | Medium | human_reviewable_pending_poc | n/a (Medium) | **= official H-13 (High)** — real finding, under-rated |
| ZETA-12 | Medium | human_reviewable_pending_poc | n/a (Medium) | non-awarded (MEV/deadline QA-class) |

## Safety invariants — all satisfied
- **0 High/Critical entered without L3 PASS/override** (7 Highs were blocked-from-queue and recorded in `_manifest`).
- **0 dangerous false-Highs queued** (every entry is Low/Medium).
- 100% of entries carry `human_review_required=true` and submit nowhere.

## Correctness vs answer key
- **1/3 entries is a real official finding** (ZETA-04 = H-13) — but queued at Medium, so a human reviewer would still
  catch the under-rating before any submission.
- **2/3 entries are non-awarded low/QA** (ZETA-07, ZETA-12) — `false_queue_entries (false-Highs) = 0`; non-awarded-low
  = 2. None would have caused a bad submission (all low, all human-gated).
- The genuine Highs that the queue *should ideally* carry as High (H-13, H-10) were **kept out of the High lane** by L3
  (no executed PoC) — correct fail-closed behavior, at the cost of recall.
