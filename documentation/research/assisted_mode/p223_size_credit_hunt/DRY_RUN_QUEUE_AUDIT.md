# P223 — Dry-run submission queue audit (Step 8)

Local-only queue: `output_research/dry_run_submission_queue/SC-0{1,3,4}.json` + `p223_queue.jsonl` +
`p223_manifest.json`. **Submits nowhere.** (P215's `queue.jsonl`/`_manifest.json`/`ZETA-*.json` left
byte-identical — P223 uses a separate ledger/manifest.)

## Entries (3)
| id | severity_rec | readiness | l3_status | human_review | external_submission | submitted |
|----|--------------|-----------|-----------|--------------|---------------------|-----------|
| SC-01 | high | human_review_required_l3_pass_precondition_noted | PASS | true | false | false |
| SC-03 | medium | human_reviewable_pending_harness | NEEDS_HARNESS | true | false | false |
| SC-04 | medium | human_reviewable_pending_harness | NEEDS_HARNESS | true | false | false |

## Safety invariants (manifest-verified)
- `high_with_l3_pass = 1` (SC-01, executed PoC) · **`high_without_l3_pass = 0`** (no unproven High queued).
- `all_human_review_required = true` · `all_external_submission_false = true` · `all_research_only = true` ·
  `submitted_count = 0`.
- SC-01 is queued for **human severity calibration** (Medium-vs-High given the resident-ETH precondition), not
  as an auto-High — the L3-PASS High is advisory. This is the conservative routing that honors the
  0-false-High invariant while still surfacing the proven mechanism above noise.
- The 9 downgraded Lows are not queued (below the queue bar), consistent with the recall-first / precision-second
  funnel.
