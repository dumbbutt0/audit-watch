# P147 — Prompt-derived vs Runtime-confirmed Status (kept strictly separate)

The centrifuge holdout item is **runtime-only**: it lives in the research sidecar, NOT in the prompt corpus — so it
has no prompt-derived score and does not affect the prompt scorecard.

| field | value |
|---|---|
| bug_id | H1-centrifuge-userescrow |
| architecture | centrifuge (holdout) |
| target | UserEscrow.transferOut |
| **prompt_decision** | n/a (not a prompt-corpus item) |
| **runtime_status** | **runtime_confirmed** |
| runtime_confidence | high |
| runtime_harness_type | real_contract |
| corrected_reference_type | strict_receiver_equals_destination |
| control_case | receiver_equals_destination |
| vulnerable_output | paid receiver 0xBEEF 1000e18 (destination got 0) |
| corrected_output | revert (receiver must be destination) |
| **duplicate_status** | **duplicate_unknown** |
| runtime_only | true |
| routing_allowed | false |
| submission_ready | false |
| requires_human_review / requires_poc_review | true / true |

## Separation guarantees
- Recorded only in `output_research/value_provenance_eval/runtime_status.jsonl` (now B1 + B5 + this). It is a
  **runtime-only** panel row — `build_runtime_panel` surfaces sidecar `bug_id`s not in the corpus without adding
  them to the corpus, so the prompt scorecard (`per_arch`/`totals`/`runs`) is byte-for-byte unchanged
  (`integrity.prompt_corpus_unchanged: true`).
- `runtime_confirmed` ≠ submission-ready and ≠ a prompt finding. It is mechanism evidence for an intent-dependent,
  duplicate-unknown item that **requires human severity/validity review**.
