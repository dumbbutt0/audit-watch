# P140 — Current Queue Map (pre-P140 state, verified by inspection)

| Aspect | Value |
|---|---|
| Job id format | `advisory_id` = `VP-{contract}.{function}` (`run_value_provenance_advisories.py build()`) |
| Queued packet | `output/value_provenance_jobs/<advisory_id>.md` (neutral, answer-key-free) |
| Results file | `output/value_provenance_advisory_results.json` → `{ran, summary, results:[...]}` |
| Pending entry fields | `auto_run_status=pending_manual_execution`, `prompt_decision=pending`, `advisory_only/submission_ready=false/requires_human_review`, `output_path`, `allowed_next_steps`, `forbidden_next_steps`, `mechanism_summary`, `source_evidence_summary` |
| Review-gate render | `generate_review_gate.py._value_provenance_section()` (robust; never added to `findings`) |
| Existing result writer | `deep_pass_write.py --eval` — distinct schema (`decisions[]` → scorer candidates); the "validate-then-record, never confirm" precedent, but NOT the right ingestion input for advisory VP completion |
| Completion/ingestion writer | **did not exist** → P140 adds it |

## What P139 produced vs what P140 needed
- P139 produced the **pending** half: queued packets + a `results[]` of `pending_manual_execution` entries.
- The missing half: a deterministic way to read an operator's manual `/deep-pass` result, validate its safety,
  match it to a pending job by `advisory_id`, flip status to `completed`/`failed`, and re-render — without ever
  confirming or making anything submission-ready.

## Design choice
**Option A** (extend `run_value_provenance_advisories.py` with `--ingest-results`) over Option B (new script):
the script already owns the results file, the config loader, `audit_path`, and a fail-open `main()`. A single
source of truth keeps the queue + completion logic cohesive and the test surface small.
