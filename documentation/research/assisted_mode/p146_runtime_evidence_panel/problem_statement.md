# P146 — Problem Statement

P143 (noya B1) and P145 (blackhole B5) produced real-contract runtime confirmations, recorded in the research-only
sidecar `output_research/value_provenance_eval/runtime_status.jsonl`. The P142 harness scorecard reports only
**prompt-derived** metrics (`per_arch` / `totals` / `runs`) and had no view of runtime evidence.

**P146 adds a research-only runtime evidence panel to the P142 scorecard** — surfaced *alongside*, never *inside*,
the prompt metrics. It must not change prompt numbers, routing, severity, submission gates, or any production
behavior, and the harness stays un-wired.

## What was built
- A `runtime_panel` (one row per corpus item) with the requested fields (`runtime_status`, `runtime_confidence`,
  `bug_id`, `architecture`, `bug_class`, `harness_path`, `real_contract_deployed`, `production_source_modified`,
  `corrected_reference_type`, `control_case`, `vulnerable_output`, `corrected_output`, `divergence_summary`,
  `limitations`, `duplicate_status`, `routing_allowed`, `submission_ready`).
- Backfill of **B1** and **B5** as `runtime_confirmed` / `high` (from the sidecar); every other corpus item
  defaults to `runtime_status=not_run` / `runtime_confidence=none`.
- The panel is emitted as an additive `runtime_panel` key in `scorecard.json`, a standalone `runtime_panel.json`,
  and a "Runtime Evidence Panel" section in `scorecard.md`. A `runtime-panel` subcommand was added (+ included in
  `all`).

## Guarantee
The prompt-derived metrics are **value-for-value unchanged** (`finding 3 / needs_human 1 / strong_clear 7`,
`useful_recall 0.80`, `clean_false_finding_rate 0.0`) — proven by an integrity test that builds the scorecard with
an empty vs a populated sidecar and asserts `per_arch` / `totals` / `runs[*].totals` are identical. Every panel row
is forced `routing_allowed=false` / `submission_ready=false`.
