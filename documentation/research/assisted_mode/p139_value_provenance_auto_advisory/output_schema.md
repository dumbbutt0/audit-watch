# P139 — Output Schema

`output/value_provenance_advisory_results.json` = `{ran, generated_at, llm_available, config, summary, results[]}`.
Each `results[]` entry:
`advisory_id, audit_id, contract, function, file_path, source_detector_or_recommendation, recommended_prompt,
auto_run_status (completed|pending_manual_execution|skipped|failed|timed_out), advisory_only=true,
submission_ready=false, requires_human_review=true, prompt_decision (finding|likely_exploitable|needs_human|
strong_clear|pending|error|unknown), prompt_confidence, mechanism_summary, source_evidence_summary,
rejected_alternatives, safety_notes, allowed_next_steps, forbidden_next_steps, output_path (the queued job .md),
error`.

Queued job: `output/value_provenance_jobs/<advisory_id>.md` = deep_pass prompt reference + neutral source bundle.
In api-free mode `auto_run_status=pending_manual_execution` and `prompt_decision=pending` (never fabricated).
