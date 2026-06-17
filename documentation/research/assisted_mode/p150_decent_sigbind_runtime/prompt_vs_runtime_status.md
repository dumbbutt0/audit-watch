# P150 — Prompt-derived vs Runtime Status (kept strictly separate)

The decent item is **runtime-only**: it lives in the research sidecar, NOT the prompt corpus — no prompt score, no
effect on prompt metrics.

| field | value |
|---|---|
| bug_id | H3-decent-utbfeecollector-sigbind |
| architecture | decent (holdout) |
| target | UTBFeeCollector.collectFees |
| **prompt_decision** | n/a (not a prompt-corpus item) |
| **runtime_status** | **runtime_confirmed** (mechanism) |
| runtime_confidence | high |
| runtime_harness_type | real_contract |
| suspected_mechanism | signature-not-bound-to-executed-fees (authorization subject mismatch) |
| corrected_reference_type | bind_fees_to_signed_packedInfo |
| control_case | matched_fees_no_divergence |
| vulnerable_output | charged 1000e18 (unsigned) vs signer-authorized 1e18 |
| corrected_output | revert (fees not bound to signature) |
| **duplicate_status** | duplicate_unknown |
| runtime_only | true |
| routing_allowed | false |
| submission_ready | false |
| requires_human_review / requires_poc_review | true / true |

## Separation guarantees
- Recorded only in `output_research/value_provenance_eval/runtime_status.jsonl` (now B1, B5, H1, H2, H3). It is a
  **runtime-only** panel row — `build_runtime_panel` surfaces it without adding it to the corpus, so the prompt
  scorecard (`per_arch`/`totals`/`runs`) is byte-for-byte unchanged (`integrity.prompt_corpus_unchanged: true`).
- `runtime_confirmed` = the contract-level binding-failure **mechanism**; it is **not** a severity claim and not
  submission-ready. Reachability/severity (onlyUtb + UTB flow + replay) is deferred to human review.
- Panel now spans 5 architectures and the full vocabulary: `runtime_confirmed: 4`, `runtime_refuted: 1`,
  `not_run: 9`.
