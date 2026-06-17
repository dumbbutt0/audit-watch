# Literature Synthesis — Agentic AI Workflows

> **Source caveat:** synthesized from training knowledge (cutoff ~Jan 2026). These are **not live
> citations** — names are for orientation; verify before quoting externally. Where the user wants live
> sources, `experiment_design.md`/roadmap note WebFetch as an optional follow-up.

Organized by the agentic-workflow building blocks relevant to a security-audit pipeline, each mapped to
**where Audit-Watch already uses it** and **the gap it could close** (per Phase-13's generalization wall).

## 1. Reasoning / acting loops

| Pattern | Idea | Audit-Watch today | Gap it could close |
|---------|------|-------------------|--------------------|
| **ReAct** (reason+act, tool-use interleaved) | LLM alternates thought ↔ tool call | the specialist agents already "think + call `retriever.py`/`immunefi_retriever.py`/MCP" | a deep-pass agent that interleaves source-reads + `simulate_tx`/`get_storage` to *prove* a value-flow path |
| **Reflexion / self-critique** | agent critiques its own output, retries | `/confirm` multi-pass (3–5 independent re-confirmations) is a coarse ensemble form | a critic that demands a concrete attacker-path *disproof* before a "clear" (the no-silent-clear rule, but agentic) |
| **Plan-and-execute / decomposition** | a planner splits a task into typed sub-steps | the `/deep-analysis` 8-substage plan (invariants → interactions → traces) is exactly this | apply the same decomposition to a *single candidate* (provenance → manipulation → consumer → impact) |
| **Tree/Graph-of-Thought** | explore multiple reasoning branches, prune | not used | exploring attacker variants per candidate (higher cost; reserve for High/Critical) |

## 2. Multi-agent orchestration

- **Specialist ensembles** (one agent per concern) — Audit-Watch's 34 `agents/*.md` are this pattern
  (reentrancy/oracle/access/…). Literature (AutoGen / CrewAI / MetaGPT / LangGraph-style graphs) emphasizes a
  **router + typed message contracts + a judge**. Audit-Watch's router is `attack_surface.json` scoring +
  `deep_pass_queue.py` tiering; its judge is `judge_simulate.py` (5-persona). **Optimization opportunity:**
  make the deep-pass a *graph* (router → specialist → critic → write) with deterministic finalizers, mirroring
  the existing prepare→skill→write triplet.
- **Debate / cross-examination** — multiple agents argue a finding's validity. Audit-Watch's closest analog is
  multi-pass confirm + the 5-persona judge. Honest note from the literature: debate helps *calibration* more
  than *recall*; useful for FP-suppression (which Audit-Watch already does well), less for the generalization
  gap (which is about *finding* the bug at all).

## 3. Retrieval & grounding

- **RAG / tool-grounded reasoning** reduces hallucination by anchoring on retrieved facts. Audit-Watch's
  `kb-search` MCP (local Chroma Solodit/C4/Sherlock KB + `attack_primitives.json`, incl. the new `PRIM-021`)
  and `immunefi` MCP are this. **Key for agentic recall:** grounding a deep-pass in *retrieved precedents of
  the candidate's shape* (e.g., "wrong-index in nested loops") gives the LLM a concrete template to match —
  directly relevant to the wrong-value generalization gap.
- **On-chain grounding** — `onchain-context` MCP (`simulate_tx`, `get_storage`, `get_tvl`) lets an agent
  *verify* a hypothesized exploit/state rather than assert it. The literature's "verifier/executor" theme;
  Audit-Watch already has the connector, under-used at the deep-pass stage.

## 4. Verification, judging, self-consistency

- **LLM-as-judge** (well-known calibration + bias caveats: verbosity bias, self-preference, position bias) —
  Audit-Watch uses 5-persona `judge_simulate.py`. The literature's caution (judges overfit to style) reinforces
  the repo's choice to keep the judge *advisory* and human-gated.
- **Self-consistency / sampling ensembles** — sample N reasonings, majority-vote. Audit-Watch's multi-pass
  confirm (threshold 0.6) is this. Cheap recall booster *if* the base agent can find the bug at least sometimes.

## 5. Evaluation methodology (the most important literature for this project)

- **Benchmark contamination / overfitting** is the dominant failure mode in agentic-eval papers: agents tuned
  on a benchmark report inflated numbers that don't transfer. **This is precisely Phase 12/13's finding**, and
  why the **train/holdout split + Holdout-Recall-primary** discipline is mandatory for any agentic step here.
- **Pass@k / cost-normalized metrics** — agentic recall must be reported against **cost/latency** (and, here,
  the `api_free` constraint), not just raw recall. The roadmap adopts cost-normalized KPIs.
- **Agentic security-audit work** (LLM-for-smart-contract-audit line — GPTScan-style static+LLM, LLM4Vuln-style
  knowledge-augmented detection, and recent "autonomous exploit/audit agent" work) consistently reports: LLMs
  add *recall on semantic bugs* deterministic tools miss, but at the cost of FP/hallucination — requiring a
  *verifier* (PoC/sim) and a *human gate*. Audit-Watch's L1–L3 PoC standard + human-review queue already encode
  this; the deep-pass is where the *recall* half would attach.

## Net takeaways for Audit-Watch

1. The literature's recall gains come from **tool-grounded reasoning over a focused candidate** (ReAct + RAG +
   on-chain verify), not from more agents. That matches the `deep_pass_queue` design.
2. Every recall claim must be **holdout-measured and cost-normalized** — the field's repeated lesson, and
   Phase-13's lived experience.
3. FP-suppression machinery (judge, multi-pass, no-silent-clear) is already strong; the open frontier is
   **agentic recall on the bugs the deterministic lenses can't generalize to** (wrong-value, semantic invariants).
