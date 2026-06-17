# P146 — Panel Design

## Principle
The runtime panel is **supplemental** and derives **only** from the corpus (`corpus.jsonl`) + the runtime sidecar
(`runtime_status.jsonl`). It never reads or writes the per-architecture queues, so it is **structurally incapable**
of changing the prompt-derived metrics (`per_arch` / `totals` / `runs`), which are computed solely from the
queues + ingestion reports.

## Code (`scripts/research/value_provenance_eval_harness.py`, additive)
- `DEFAULT_CFG += runtime_status_path` (default `output_research/value_provenance_eval/runtime_status.jsonl`).
- `RUNTIME_STATUS = {not_run, partial, runtime_confirmed, runtime_refuted, inconclusive}`,
  `RUNTIME_CONFIDENCE = {none, low, medium, high}`.
- `_load_runtime_sidecar(cfg)` → `{bug_id: row}` (jsonl, fail-open).
- `build_runtime_panel(cfg)` → one row per corpus item: default `not_run`/`none`, overlaid with the sidecar by
  `bug_id`; out-of-vocab `runtime_status`→`inconclusive`, `runtime_confidence`→`none`; **forces**
  `routing_allowed=False` + `submission_ready=False` on every row (research invariant); emits a `summary`
  (`by_status`) + an `integrity` block + the four research flags.
- `runtime_panel(cfg, workdir)` writes standalone `runtime_panel.json` + `runtime_panel.md`.
- `scorecard()` computes `per_arch`/`totals`/`runs` **unchanged**, then adds `out["runtime_panel"]` (additive key)
  and appends the panel section to `scorecard.md`.
- `main`: new `runtime-panel` subcommand; `all` runs seed → ingest → scorecard (which now also emits the panel).

## Data (`runtime_status.jsonl`, research-only — single source of runtime truth)
B1 and B5 rows enriched with the full P146 field set (architecture, bug_class, harness_path,
corrected_reference_type, control_case, vulnerable/corrected_output, divergence_summary, limitations,
duplicate_status, runtime_status, runtime_confidence). All 9 other corpus items have no sidecar row → default
`not_run`.

## Config
`config/research/value_provenance_eval_harness.json += runtime_status_path` (research-only; no production config
touched).
