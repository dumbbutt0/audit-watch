---
name: deep-analysis
description: "Credit-free, skill-in-session replacement for run_deep_analysis.py (Step 0 deep invariant analysis). Reasons over the bundle built by deep_analysis_prepare.py — extracting protocol invariants, mapping cross-system interactions, and tracing whether dangerous chains can violate invariants — then writes the canonical Step-0 artifacts in-session and validates with deep_analysis_write.py. Activate when user says: /deep-analysis, deep analysis, run deep invariant analysis, Step 0 without API, deep trace, or when run_pipeline.sh pauses analyze for the /deep-analysis skill."
---

# Deep Analysis (skill-in-session)

Does the work the eight Step-0 substages (`extract_invariants`, `map_interactions`, `deep_trace`,
`backward_trace`, `multi_tx_trace`, `escalate_threads`, plus optional fuzzing/SMT harness writers)
delegate to Claude API calls — but **in this session**, so it costs no API credits. The reasoning
specs are the existing prompts under `prompts/`; you apply them in-session and write the same
canonical artifacts the API scripts produce.

## When to use

When `./run_pipeline.sh analyze` pauses for deep analysis (api-free mode), or any time the user wants
Step 0 without spending credits. Routing: `scripts/llm_runtime.py` SKILL_MAP `deep_analysis → /deep-analysis`.

## Procedure

1. **Prepare the bundle (deterministic):**
   ```
   python scripts/deep_analysis_prepare.py --contract <path_or_dir> [--mode deep]
   ```
   Writes `data/invariants/_bundles/index.json` with: `scope_files` (paths + line counts),
   `static_summary`, `prompt_dir`, `substage_plan` (each substage's prompt + exact output paths),
   and `optional_tool_stages`. No source is embedded — you read source files yourself via Read.

2. **Read the bundle index**, then **execute each substage in `substage_plan` order, in-session.**
   For each substage, open its prompt under `prompt_dir` and apply it literally, reading the scope
   files you need via the Read tool. Write outputs to the **exact paths** in the plan, using the
   documented schema (below). Do not call any API script (`extract_invariants.py`, `deep_trace.py`,
   etc.) — a PreToolUse hook blocks them; you produce the artifacts directly.

   **0a — Invariants** (`prompts/invariant_extractor.md`) → write a JSON **array** to
   `data/invariants/protocol_invariants.json`; each item: `invariant_id, category, statement,
   formal_expression, state_variables_involved[], mutating_functions[], violation_consequence,
   suspicion_score (1-5)`. Also write the `suspicion_score >= 4` subset to `high_suspicion.json`
   and the `== 3` subset to `medium_suspicion.json`.

   **0b — Interactions** (`prompts/interaction_mapper.md`) → write a JSON **object** with keys
   `call_graph[]`, `interaction_chains[]`, `trust_boundary_crossings[]` to
   `data/interactions/call_graph.json`; write the `danger_score >= 4` chains to `dangerous_chains.json`.

   **0c/0c-bis/0f — Tracing** (`prompts/deep_trace.md`) → for each high-suspicion invariant × dangerous
   chain (and, for multi_tx, each STATE_MACHINE invariant across transactions), trace per the prompt and
   append one thread object per line to `data/threads/promising_threads.jsonl` (verdict ≠ `DEAD_END`)
   or `data/threads/dead_ends.jsonl` (verdict `DEAD_END`). Thread fields: `thread_id, invariant_id,
   chain_id, verdict (CRITICAL_THREAD|HIGH_THREAD|MEDIUM_THREAD|DEAD_END|NEEDS_MORE_CONTEXT),
   entry_conditions, violation_path[], attacker_class, impact_estimate, evidence`. Prefix multi-tx
   threads `MT-`. **Honor the `skips` map** (skip backward/multi-tx if flagged).

   **0d — Escalate** (`prompts/impact_chain_escalation.md`) → convert each non-dead-end thread to a
   finding and write `output/findings_deep_trace.json` as `{"agent":"deep_trace","contract":<path>,
   "findings":[...]}` (finding fields match the Step-2 agent schema: id, title, severity, confidence,
   description, location, impact, ite, ice_chain).

   **Optional tool stages** (only if `optional_tool_stages` enables them): write the Echidna harness /
   Z3 encoding the deterministic runners expect; the runners themselves are not LLM and stay as-is.

   Be rigorous and zero-trust: if you cannot fully trace a hop, mark the thread `NEEDS_MORE_CONTEXT`
   rather than guessing. An honest `DEAD_END` with a reason is worth more than a fabricated thread.

3. **Validate + finalize (deterministic):**
   ```
   python scripts/deep_analysis_write.py
   ```
   It checks every core artifact exists, parses, and has the right shape, then writes
   `data/invariants/_deep_analysis_complete.json`. If it reports a gap, fill it and re-run — never
   leave Step 0 half-written, because every Step-2 specialist reads these artifacts.

## Output

Report counts: invariants (total / high / medium), interaction chains (total / dangerous),
threads (promising / dead-ends), deep-trace findings. Then tell the user to continue with
`./run_pipeline.sh analyze-resume`.
