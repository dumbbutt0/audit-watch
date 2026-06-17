# P142 — Harness Design

## Component
`scripts/research/value_provenance_eval_harness.py` (NEW; research-only, un-wired). Invariant: **"Aggregate,
don't adjudicate."**

## Subcommands (all write only under the research workspace, default `output_research/value_provenance_eval/`)
- **`seed [--arch X | --all] [--workdir D]`** — from `corpus.jsonl`, build a pending queue per architecture at
  `<workdir>/<arch>/value_provenance_advisory_results.json`. Each entry:
  `queue_origin:eval_only_manual_queue`, `auto_run_status:pending_manual_execution`, `prompt_decision:pending`,
  the advisory triplet, the item's `item_id`/`label`, and the four research flags + `routing_allowed:false`.
- **`ingest [--arch X | --all]`** — for each corpus row WITH provenance (`blind_output_ref` + valid
  `recorded_decision`), build a completion artifact from the **recorded real outcome** (`execution_mode:
  replayed_recorded_blind`, `completed_at: replayed:<phase>` = deterministic), then run all artifacts through the
  production **`ingest_results()`** (imported as a library) so the P140 safety validator + forced advisory triplet
  are reused verbatim. Writes the completed queue + an ingestion report. Provenance-less / invalid-decision rows
  are **refused** (recorded in `refused_no_provenance`), never fabricated. Operator-supplied live result files for
  new items work the same way.
- **`scorecard [--append]`** — aggregate completed queues across architectures into `<workdir>/scorecard.json`
  (+ `scorecard.md`): per-arch + totals `{queued, completed, finding, likely_exploitable, needs_human,
  strong_clear, error, clean_strong_clear, clean_false_finding, buggy/clean, buggy_useful/strict, rejected}` plus
  derived `{useful_recall, strict_recall, clean_false_finding_rate}`; a `runs[]` time-series grows on `--append`.
- **`all`** — `seed` → `ingest` → `scorecard --append` in one shot.

## Safety mechanics
- **Four research flags + `routing_allowed:false`** stamped on every queue, ingestion report, and scorecard;
  re-applied after the merge so they survive `ingest_results`.
- **Defensive guard `_refuse_if_routed`** (mirrors `evidence_bundle_gate.py`): refuses any config/queue with
  `routing_allowed != false`, `routes_in_production:true`, or non-empty `routed_manifest_ids`.
- **Fail-open**: missing corpus/workspace → safe no-op; malformed corpus line → skipped; `main()` swallows
  unexpected errors (a research instrument must never wedge a workflow).
- **Idempotent**: deterministic artifact fields (incl. `completed_at`) → re-ingest yields identical entries.

## Reuse (no production change)
Imports `ingest_results` + `DEFAULT_CFG` from `scripts/run_value_provenance_advisories.py` as a **library** only.
Adds **zero** lines to the production VP script, review gate, `agent_policy.json`, or `run_pipeline.sh`. The
un-wired invariant is about *routing*, not code isolation — grep proves the harness/config name appears in neither
`run_pipeline.sh` nor `agent_policy.json`.

## Config (research-only) — `config/research/value_provenance_eval_harness.json`
`{enabled, corpus_path, workdir, is_gate:false, research_only:true, routes_in_production:false,
routed_manifest_ids:[], routing_allowed:false}`. The script also has a built-in `DEFAULT_CFG` fallback; research
flags are re-forced after any config load.
