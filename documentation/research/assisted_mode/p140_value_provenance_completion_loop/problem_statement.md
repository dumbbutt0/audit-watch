# P140 — Problem Statement

P139 (ACCEPT_SCAFFOLD) auto-prepares + routes H-03-class value-provenance deep-pass jobs as **advisory-only**.
Because `config/runtime_policy.json api_free=true` ⇒ `llm_runtime.llm_available()=False`, jobs are queued
`auto_run_status=pending_manual_execution` / `prompt_decision=pending` and executed via the in-session `/deep-pass`
skill — there is no non-interactive runner and P139 correctly did not invent one.

**Gap P139 left open:** once an operator actually runs a queued job, there was **no deterministic local path** to
fold that manual result back into the advisory record and re-render review. The queue could be created but never
*completed*.

**P140 closes that loop:** queued job → manual deep-pass result artifact → advisory status update → review-gate
rendering — **without any unsafe promotion**. This is a queue-completion + status-ingestion phase, NOT an
autonomous-LLM phase.

## Primary question
Can the pipeline close the loop from queued value-provenance job → manual deep-pass result → advisory status
update → review-gate rendering, deterministically and locally, without converting prompt output into confirmed /
submission-ready findings?

## Answer (measured)
Yes. Ingestion is deterministic, local, idempotent, fail-open; it quarantines any unsafe/malformed artifact and
**forces** `advisory_only=true / submission_ready=false / requires_human_review=true` on every merged entry.
Completed results render in a clearly-labelled advisory-only review-gate subsection (findings tagged
"NOT confirmed", strong_clears shown as cleared advisory context), are never added to Validated Findings, and
never change the confirmed-findings count.
