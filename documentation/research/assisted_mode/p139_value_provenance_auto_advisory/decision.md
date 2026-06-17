# P139 — Decision

## Decision: **ACCEPT_SCAFFOLD**

The api-free pipeline (`config/runtime_policy.json api_free=true` → `llm_runtime.llm_available()=False`) has **no
safe non-interactive LLM runner**, so the prompt cannot be executed by a `run_pipeline.sh`-invoked script. Per
the guardrail, P139 does **not** invent one: it implements an honest auto-prepare + auto-route **scaffold** —
the H-03-class value-provenance recommendation is automatically turned into a queued deep-pass job
(`auto_run_status=pending_manual_execution`, `prompt_decision=pending`, never fabricated), surfaced ADVISORY-ONLY
in `review_gate.md`, with EXECUTION left to the in-session `/deep-pass` skill. No unsafe promotion, no clean-FP
inflation, all safety constraints met.

### Rubric
- Not ACCEPT_AUTO_ADVISORY: non-interactive execution is unavailable (api-free) — claiming full auto-run would be
  faking it.
- **ACCEPT_SCAFFOLD** ✅: the packet/job/results/render path is correct and honest; H-03 target surfaced safely.
- Not ACCEPT_EVAL_ONLY: the scaffold is safe at the production default (advisory-only, pending, non-blocking,
  capped) — no need to restrict to eval; research-only stays research-only.
- Not TUNE_AND_RETEST: the trigger was tightened during measurement (exact span + value-conversion-in-loop) and
  now precisely surfaces the H-03 class with 0 config-setter false triggers.
- Not REJECT_OR_DEFAULT_OFF: nothing prompt-derived can be mistaken for confirmed/submission-ready.

## Final response

**What changed** — new `scripts/run_value_provenance_advisories.py` (config-gated, capped, fail-open scaffold) +
`value_provenance_auto_run` config block + a "Value Provenance Deep-Pass Results — advisory only" subsection in
`generate_review_gate.py` + a non-blocking pipeline call after surfacing, before the review gate. +14 tests.

**What stayed unchanged** — detectors, severity, submission, gate pass/fail, confirmed count, Validated Findings;
research-only stays research-only; no non-interactive runner invented; P130–P138 preserved.

**Trigger rules** — recommended_prompt ∈ allowed_prompts AND a re-verified value-conversion-in-loop signal on the
EXACT function span, excluding mock/trivial/confirmed/submission_ready (+research-only unless enabled), capped.

**Auto-run or scaffold result** — SCAFFOLD: jobs queued as `pending_manual_execution` (no faked LLM run);
executed via the in-session `/deep-pass` skill, recorded via `deep_pass_write.py --eval`.

**Review-gate rendering** — advisory-only subsection with status + "requires human review and PoC" disclaimer;
never in Validated Findings; confirmed count unchanged.

**Noya measurement** — 2 value-provenance jobs incl. the H-03 `NoyaValueOracle._getValue` target; config-setter
loops correctly excluded; all advisory_only/submission_ready=false/requires_human_review=true; rendered;
confirmed count 0 unchanged; not in Validated Findings; no pipeline block; master gate off → ran:False.

**Safety** — all 16 constraints met; pending-not-faked; fail-open; advisory-only; human + PoC mandatory.

**Tests** — 14 new pass; `bash -n` clean; full suite 1621 passed / 2 pre-existing snapshot fails / 4 skipped;
self-test OK.

**Integrity** — only the 5 planned files changed; active audit restored to `quantamm-2024-12-eval`; noya state
restored.

**Decision** — ACCEPT_SCAFFOLD.

**Next recommended phase (P140)** — close the execution loop honestly: have the operator run the in-session
`/deep-pass` skill on the queued value-provenance jobs and record results via `deep_pass_write.py --eval`, then
auto-update `value_provenance_advisory_results.json` (pending → completed/strong_clear/needs_human) and re-render
review_gate — measuring end-to-end how many queued jobs convert to confirmed-looking findings vs clears. Only if
a real non-interactive runner is ever added (api_free=false + sanctioned key) would the `completed` auto-run path
activate; until then the scaffold + in-session skill is the safe path.
