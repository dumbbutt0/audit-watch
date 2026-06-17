# P140 — Operator Workflow

The completion loop is **operator-driven** (no autonomous LLM). The pipeline prepares + renders; a human runs the
prompt in-session and records the result; ingestion folds it back deterministically.

1. **Run the gate.** `./run_pipeline.sh full` (or `review-gate`) → writes `output/review_gate.md` with the
   "Value Provenance Deep-Pass Results — advisory only" subsection listing queued jobs as
   `pending_manual_execution`.
2. **Inspect queued jobs.** Read `output/value_provenance_jobs/<advisory_id>.md` — each is a neutral,
   answer-key-free source bundle referencing `prompts/deep_pass_value_provenance.md`.
3. **Run the approved skill in-session.** Execute the `deep_pass_value_provenance` `/deep-pass` skill on the
   bundle. (api-free has no non-interactive runner — execution stays in-session by design.)
4. **Save the result.** Write one JSON per job into `output/value_provenance_manual_results/` using the
   completion schema (`completion_schema.md`). `job_id` must equal the queued `advisory_id`. Keep
   `advisory_only:true / submission_ready:false / requires_human_review:true`.
5. **Ingest.** `python scripts/run_value_provenance_advisories.py --ingest-results`
   → updates `output/value_provenance_advisory_results.json` (pending → completed/failed) and writes
   `output/value_provenance_ingestion_report.json` (accepted / rejected / unmatched). Unsafe or malformed
   artifacts are quarantined (reported, job stays pending). Idempotent — safe to re-run.
   *(Steps 1 and `full`/`review-gate` also run this automatically; the manual command is for re-ingesting.)*
6. **Re-render.** `python scripts/generate_review_gate.py` → the completed rows show with decision/confidence/next
   step; findings are tagged **NOT confirmed**, strong_clears as cleared advisory context.
7. **Human decision (mandatory).** For each completed entry choose: **reject** · **keep advisory** · **build PoC**
   · **escalate to human review**. Nothing here is submission-ready; a High/Critical real-world submission still
   requires the Level-3 PoC standard + human sign-off.

## Notes
- To hide cleared rows: set `auto_run_value_provenance_hide_strong_clear: true`.
- To disable the loop entirely: `auto_run_value_provenance_advisories: false` or `mode: off`.
