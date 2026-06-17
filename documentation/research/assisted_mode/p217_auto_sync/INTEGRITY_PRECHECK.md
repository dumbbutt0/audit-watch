# P217 — INTEGRITY PRECHECK (START)

Captured 2026-06-07, before any change. md5 first-8.

| File | START | expected END |
|------|-------|--------------|
| `scripts/dashboard_sync.py` | `26bd7ee0` | unchanged |
| `scripts/build_synced_findings.py` | `a7853775` | **CHANGE** (refactor → thin shim over the wrapper) |
| `scripts/funnel.py` | `d9f09981` | unchanged |
| `scripts/finding_detail.py` | `f12aa8d3` | unchanged |
| `scripts/findings_overview.py` | `5c6cccb5` | unchanged |
| `scripts/dashboard.py` | `197ac4d5` | unchanged |
| `scripts/submission_readiness_review.py` | `e4960878` | unchanged |
| `scripts/final_submission_pack.py` | `57cba16d` | unchanged |
| `documentation/research/funnel/funnel_records.json` | `b3278eed` | unchanged |
| `documentation/research/funnel/synced_findings.generated.json` | `eb359941` | **CHANGE** (regenerated, richer; same 12 ids) |
| `config/runtime_policy.json` | `bea43487` | unchanged (`api_free:true`) |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | unchanged |
| `prompts/deep_trace.md` | `ef93a6c2` | unchanged (forbidden) |
| `scripts/min_confirm_gate.py` | `41dd3c96` | unchanged (forbidden) |
| `scripts/confirm_gate.py` | `4fadfc5f` | unchanged (forbidden) |

## Confirmed
- `api_free: true`.
- No live route-to-submit; no dashboard submit/promote controls (P216-verified; HTML unchanged here).
- Active-audit switching not required to view synced records (global funnel track); current active = zetachain-2023-10-holdout (irrelevant to the read path).

## BEFORE completeness (P216 mirror, the baseline to beat)
Aggregate evidence completeness **57% (144/252)** across 12 records / 21 evidence fields. Per-record 47–61%.
Recoverable unknowns present in the artifacts: `root_cause`, `attacker_model`, `exploit_steps`, `function_map`,
`defense_map`, `intent_scope_operator_assumptions`, `red_flags`. (`novelty_duplicate` stays unknown — no source.)

## Scope guarantee
Only the generated mirror + `build_synced_findings.py` (shim) change. `dashboard_sync.py`, `funnel.py`,
`finding_detail.py` and all other tracked/forbidden files byte-identical START==END.
