# P149 — Integrity Checks

| check | result |
|---|---|
| Production source unchanged | ✓ `UserEscrow.sol` byte-identical (2330 bytes); read-only review of LiquidityPool/InvestmentManager (no edits) |
| Prompt / corpus baseline unchanged | ✓ scorecard `totals` == P138 baseline byte-for-byte (finding 3 / needs_human 1 / strong_clear 7; useful_recall 0.80; clean_FP 0.0); `corpus.jsonl` untouched |
| No detector / gate / severity / submission / routing change | ✓ no code changed except the research sidecar data row + tests |
| No harness logic change | ✓ `value_provenance_eval_harness.py` unchanged (judgment fields are extra sidecar keys ignored by `build_runtime_panel`) |
| Active output symlink unchanged | ✓ `output/` → `audits/quantamm-2024-12-eval/output` |
| All runtime/panel rows routing_allowed=false & submission_ready=false | ✓ (incl. enriched H1) |
| H1 status not flipped by the judgment | ✓ `runtime_status=runtime_confirmed`, `requires_human_review=true`, `duplicate_status=duplicate_unknown` |
| Un-wired | ✓ `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty |
| External docs used | none (local source only) |

## Files touched (research-only)
- `output_research/value_provenance_eval/runtime_status.jsonl` — H1 row enriched with P149 judgment fields (data
  only; status/flags unchanged).
- `tests/research/test_value_provenance_eval_harness.py` — +2 judgment-record tests.
- `documentation/research/assisted_mode/p149_centrifuge_intent_review/` — this judgment record.

## Tests
`tests/research/test_value_provenance_eval_harness.py` → 29 passed (27 + 2 new). Full `pytest -q` → 1666 passed
/ 2 pre-existing deep_solidity snapshot fails / 4 skipped.

**submission_ready = false** (explicit end-state unless a human overrides outside this phase).
