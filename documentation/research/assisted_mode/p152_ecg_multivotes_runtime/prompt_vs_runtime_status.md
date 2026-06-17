# P152 — Prompt-derived vs Runtime Status (kept strictly separate)

H4 (ecg) is **runtime-only**: it lives in the research sidecar, NOT the prompt corpus — no prompt score, no effect
on prompt metrics.

| field | value |
|---|---|
| bug_id | H4-ecg-multivotes-accounting |
| architecture | ecg (Credit Guild, holdout) |
| target | ERC20MultiVotes.transfer / _decrementVotesUntilFree |
| prompt_decision | n/a (not a prompt-corpus item) |
| runtime_status | runtime_refuted |
| duplicate_status | duplicate_unknown |
| runtime_only | true |
| routing_allowed / submission_ready | false / false |
| conversion.outcome | runtime_refuted |

## Separation guarantees
- Recorded only in `output_research/value_provenance_eval/runtime_status.jsonl` (now B1, B5, H1, H2, H3, H4).
  `build_runtime_panel` surfaces H4 as `runtime_only` without adding it to the corpus, so the prompt scorecard
  (`per_arch`/`totals`/`runs`) is byte-for-byte unchanged (`integrity.prompt_corpus_unchanged: true`).
- The `conversion` schema is additive data on the runtime-only rows (H1-H4); it does not feed prompt metrics or
  routing.
- Panel after P152: `{rows: 15, runtime_only: 4, by_status: {runtime_confirmed: 4, runtime_refuted: 2,
  not_run: 9}}` across 6 architectures (noya/blackhole/centrifuge/velodrome/decent/ecg).
