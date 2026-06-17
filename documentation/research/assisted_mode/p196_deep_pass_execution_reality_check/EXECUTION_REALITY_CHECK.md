# P196 — Production deep-pass execution reality check (read-only)

Does the deep-pass zero-execution (P195) reflect an eval-config artifact or a real production gap? **Read-only**,
deterministic, existing artifacts only across all ~38 audits.

## Decision: `MIXED_BEHAVIOR` → **no production execution gap worth fixing; close the measurement sub-arc**
There are **two distinct deep mechanisms**, and conflating them produced P195's open question:
- **(A) budgeted candidate-queue executor** (`deep_pass_ledger.py` → `deep_pass_budget_summary` /
  `executed_deep_passes`): **executes 0 in every run, every run type.** This is **architectural, not a bug** —
  `runtime_policy.api_free=true` ("forces every stage onto its in-session skill route"; `llm_available()`=False),
  so there is **no non-interactive LLM runner** for an auto-executor. An extra eval-mode suppression sits on top
  (`agent_policy.coverage_policy.deep_pass_high_priority_block_strict_full_audit=true`,
  `waiver_discipline_strict_full_audit=true`) but is redundant given the architectural zero.
- **(B) in-session deep-analysis** (`run_deep_analysis.py` / `deep_analysis_write.py` → `findings_deep_trace`):
  the **real** deep path under api-free. It **ran in 11 eval/strict-eval runs (51 deep-trace findings total)** and
  **0 holdout (×18) / fresh (×18) / bench (×3) / other** runs.

So execution behaviour is genuinely mixed *across mechanisms and run types*, but **not** in the way the hypothesis
feared (it is the *inverse*): the eval runs received in-session deep analysis; the holdout/fresh/bench corpora
simply never had that in-session step performed.

## The five required answers
1. **Is deep-pass execution actually disabled in production-like runs?** The **budgeted auto-executor: yes —
   everywhere (0), by api-free design** (deep is routed to the in-session skill, not an auto-runner). The
   **in-session deep path is not *disabled*** — it just wasn't invoked in the holdout/fresh/bench corpora (0
   deep-trace findings), while it ran in the 11 eval runs.
2. **Is the zero-execution eval-only?** **No.** Mechanism A is 0 in **every** run type (holdout/fresh/bench/eval) —
   an architectural property, not an eval-only waiver. The `strict_full_audit` block/waiver is eval-specific but
   redundant on top of the architectural zero.
3. **What path produced the known reportables / runtime findings?** **Mechanism B** — in-session
   `run_deep_analysis.py → findings_deep_trace` (51 findings across 11 eval runs) + specialists. **Not** the
   budgeted-queue executor (A executed 0; distinct writers; A and B are artifact-distinguishable — `assigned_pass=='deep'`
   carries 0 `finding_refs`, P195).
4. **Is there a production execution gap worth fixing?** **No.** The auto-executor's zero is api-free-by-design
   (deep = in-session skill); there is no code path that silently assigns-then-drops deep execution as a defect.
   ("Production-like" in this repo means holdout/fresh/bench **research corpora** — there is no true production
   deployment run to inspect. Their lack of deep-trace is a depth-of-run/process choice, not a config bug.)
5. **Next phase — execution budget, or close the sub-arc?** **Close the measurement sub-arc.** Execution budget is
   not the lever: changing it cannot make an auto-executor run when api-free routes deep to in-session skills, and
   the real deep path already runs where the in-session step is performed.

## Skip-cause taxonomy (Q4)
Mechanism A skips decompose into: **missing-runner (api-free, structural)** + **strict/full_audit block + waiver
discipline** (eval-mode, redundant) + documented **tier × cluster × specialist** waivers
(`skipped_deep_passes_with_reason.json`). None are "accidental inconsistency"; all are intentional/architectural.

## Honesty / limits
- Mechanism A's zero-execution is **architectural (api-free)**, not a fixable code gap; do not read "budgeted
  executor = 0" as "no deep analysis happened" — mechanism B did the deep work (51 findings).
- There is **no true production run** in the repo; "production-like" = research corpora. Statements about
  "production" are inferences from architecture (api-free routing) + config, not from a deployed run.
- Every cell cites its artifact (`deep_pass_budget_summary`, `executed_deep_passes`, `findings_deep_trace`,
  `skipped_deep_passes_with_reason`, `runtime_policy.api_free`, `agent_policy.coverage_policy`). `fabrication_rate=0`.

## Sub-arc close-out
P190→P196 fully accounts for P190's apparent "87.7% upstream bottleneck": measurement noise + an answer-key
extraction defect (P193/P194, fixed) + an intentionally-architected deep-pass that runs via the in-session skill
(P195/P196). **Zero confirmed production routing / coverage / selection / execution defects remain.** The validated
production wins of the campaign are the **P183–P188 adjudication stack**. Residual open items: P194's 5
`NEEDS_HUMAN_MAPPING` + optional adoption of the P194 `eval_locus_resolver` in future answer-key builds.
