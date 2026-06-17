# P148 — Prompt-derived vs Runtime Status (kept strictly separate)

The velodrome item is **runtime-only**: it lives in the research sidecar, NOT the prompt corpus — no prompt score,
no effect on prompt metrics.

| field | value |
|---|---|
| bug_id | H2-velodrome-rewardsdist-parity |
| architecture | velodrome (holdout) |
| target | RewardsDistributor.claim / claim_many |
| **prompt_decision** | n/a (not a prompt-corpus item) |
| **runtime_status** | **runtime_refuted** |
| runtime_confidence | high |
| runtime_harness_type | real_contract |
| suspected_mechanism | B5-style claim/claim_many recipient-parity divergence |
| refuted_reason | both siblings route only via `deposit_for(_tokenId)`; no `ownerOf`/AVM/external-transfer branch; external recipient paid 0 |
| **duplicate_status** | duplicate_unknown |
| runtime_only | true |
| routing_allowed | false |
| submission_ready | false |
| requires_human_review / requires_poc_review | false / false (refuted — nothing to review) |

## Separation guarantees
- Recorded only in `output_research/value_provenance_eval/runtime_status.jsonl` (now B1, B5, H1, H2). It is a
  **runtime-only** panel row — `build_runtime_panel` surfaces it without adding it to the corpus, so the prompt
  scorecard (`per_arch`/`totals`/`runs`) is byte-for-byte unchanged (`integrity.prompt_corpus_unchanged: true`).
- The panel now spans the negative→positive vocabulary: `runtime_confirmed: 3`, `runtime_refuted: 1`,
  `not_run: 9`. A refuted row is a **killed** candidate — `requires_human_review/poc_review = false` (unlike a
  confirmed mechanism, there is nothing to escalate).
- `runtime_refuted` never routes, never submits, never sets severity.
