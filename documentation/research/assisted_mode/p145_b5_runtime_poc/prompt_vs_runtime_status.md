# P145 — Prompt-derived vs Runtime-confirmed Status (kept strictly separate)

Recorded in separate fields (constraints 9/10); runtime confirmation strengthens the advisory but does not make
the finding submission-ready and does not merge into prompt metrics.

| field | value |
|---|---|
| item_id | B5 |
| arch | blackhole |
| target | RewardsDistributor.claim_many (sibling recipient-parity / omitted AVM correction) |
| **prompt_decision** | finding |
| **prompt_status** | completed |
| prompt_source | P138 blind deep_pass + P141 ingestion |
| — | — |
| **runtime_status** | **runtime_confirmed** |
| runtime_confidence | high |
| runtime_harness_type | real_contract |
| wrong_recipient | `ownerOf` (AVM manager, 0xA814) |
| correct_recipient | `getOriginalOwner` (original owner, 0xBEEF) |
| misdirected_amount | 1e18 |
| — | — |
| duplicate | **blackhole M-04 (DUPLICATE_KNOWN)** |
| submission_ready | **false** |
| advisory_only | **true** |
| requires_human_review | **true** |
| requires_poc_review | **true** |

## Separation guarantees
- Recorded only in the research-only sidecar `output_research/value_provenance_eval/runtime_status.jsonl` (now B1
  + B5; default `not_run` for all other corpus items). It never feeds `prompt_decision`, the P142 prompt-metric
  scorecard, or production routing (carries the four research flags + `routing_allowed:false`).
- Runtime-confirmed ≠ submission-ready. B5 is the known blackhole **M-04** — this phase validates the runtime-PoC
  *method* on a second architecture; it is not a submission. Human review + scope/duplicate/severity remain
  separate gates.
