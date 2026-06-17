# P143 — Prompt-derived vs Runtime-confirmed Status (kept strictly separate)

The two evidence classes are recorded in **separate fields** (constraints 9/10). Runtime confirmation strengthens
the advisory; it does **not** merge into or upgrade the prompt metrics, and does **not** make the finding
submission-ready.

| field | value |
|---|---|
| item_id | B1 |
| target | NoyaValueOracle._getValue (multi-hop value-loop variable provenance) |
| **prompt_decision** | finding |
| **prompt_status** | completed |
| prompt_confidence | high |
| prompt_source | P137/P138 blind deep_pass_value_provenance |
| — | — |
| **runtime_status** | **runtime_confirmed** |
| runtime_confidence | high |
| runtime_harness_type | real_contract |
| runtime_result_summary | real getValue over-values a 2-hop route 20e18 vs corrected 6e18 (3.33×); controls show no divergence |
| vulnerable_output | 20e18 |
| corrected_output | 6e18 |
| delta | 14e18 |
| — | — |
| submission_ready | **false** |
| advisory_only | **true** |
| requires_human_review | **true** |
| requires_poc_review | **true** |

## Separation guarantees
- The P142 scorecard's prompt metrics (finding/strong_clear/needs_human, useful_recall, clean_FP) are **unchanged**
  — runtime status is recorded in a **separate** research-only sidecar
  (`output_research/value_provenance_eval/runtime_status.jsonl`), default `not_run` for every other corpus item.
- `runtime_status` never feeds `prompt_decision` or any prompt-metric aggregation.
- Runtime-confirmed ≠ submission-ready: scope, duplicate, and severity checks plus human review remain mandatory.
