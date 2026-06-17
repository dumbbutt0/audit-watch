# P151 — Integrity Checks

| check | result |
|---|---|
| Production source unchanged | ✓ `UTB.sol` (12509 bytes) + `UTBFeeCollector.sol` (2629 bytes) byte-identical; read-only review |
| Harness `.py` unchanged | ✓ `value_provenance_eval_harness.py` no `P151` ref; no logic change |
| No detector / gate / severity / submission / routing change | ✓ |
| No prompt / corpus baseline change | ✓ scorecard `totals` == P138 baseline byte-for-byte (finding 3 / needs_human 1 / strong_clear 7; useful_recall 0.80; clean_FP 0.0); corpus untouched |
| Active output symlink unchanged | ✓ `output/` → `audits/quantamm-2024-12-eval/output` |
| All runtime/panel rows routing_allowed=false & submission_ready=false | ✓ (incl. enriched H3) |
| H3 status not flipped | ✓ `runtime_status=runtime_confirmed`; added reachability/severity fields are data-only |
| Un-wired | ✓ `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty |
| External docs used | none (local source only) |
| No submission package | ✓ |

## Files touched (research-only)
- `output_research/value_provenance_eval/runtime_status.jsonl` — H3 row enriched with P151 reachability/severity
  fields (data only).
- `tests/research/test_value_provenance_eval_harness.py` — +2 P151 tests.
- `documentation/research/assisted_mode/p151_decent_h3_reachability_review/` — this review.

## Tests
`tests/research/test_value_provenance_eval_harness.py` → 33 passed (31 + 2 new). Full `pytest -q` → 1670 passed
/ 2 pre-existing deep_solidity snapshot fails / 4 skipped.

**submission_ready = false** (explicit end-state unless a human overrides outside this phase).
