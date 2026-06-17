# P141 — Problem Statement

P140 (ACCEPT_PARTIAL_COMPLETION_LOOP) built the value-provenance completion loop (`--ingest-results` →
`ingest_results()`): manual `/deep-pass` result artifacts are validated, matched by `job_id==advisory_id`, flipped
pending→completed/failed, rendered advisory-only in `review_gate.md`, and kept `advisory_only=true /
submission_ready=false / requires_human_review=true` (forced) — never touching confirmed counts or Validated
Findings. P140 completed **1 of 2** noya jobs and honestly left `SolvencyV2.convertAmountsToValues` pending.

**P141 is a MEASUREMENT phase** (no code/wiring/detector change). Goals:
1. Complete the remaining noya job **honestly** (one fresh uncontaminated blind deep-pass).
2. Extend the completion loop to a **second + third architecture** (blackhole, size) by reusing genuine P138
   blind `manual_in_session` outputs.
3. Observe the completion-decision distribution (finding / likely_exploitable / needs_human / strong_clear /
   error) across architectures.
4. Re-confirm advisory-only safety: confirmed count 0, nothing in Validated Findings, every result advisory-only.

## Primary questions → answers
1. **Can the remaining noya job be completed + ingested?** Yes — a fresh blind subagent cleared SolvencyV2
   (`strong_clear`, high); ingested; noya now 2/2.
2. **Does the loop work on a second/third architecture?** Yes — blackhole 3/3 and size 2/2 completed via reused
   P138 blind outputs, ingested through the unchanged P140 loop (eval_only_manual_queue).
3. **Decision distribution (7 completed):** finding 2 · likely_exploitable 0 · needs_human 1 · strong_clear 4 ·
   error 0.
4. **Rendering safe?** Yes — every architecture: confirmed count 0, nothing in Validated Findings, findings
   tagged "NOT confirmed", strong_clears as cleared advisory context.

## Honesty boundaries
- The assistant is answer-key-contaminated, so SolvencyV2 was run by a **fresh uncontaminated subagent** given
  only the neutral packet (no repo/answer-key) — the P137/P138 sanctioned blind method.
- The second/third-architecture completions **reuse real P138 blind subagent outputs** (legitimate
  `manual_in_session`); nothing was fabricated.
- All outcomes are **prompt-derived advisory evidence**; **zero are runtime-confirmed**.
