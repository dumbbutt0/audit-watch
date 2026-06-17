# Current AI Setup & Connector Inventory

Repo-accurate snapshot of the agentic stack (the "shackbots") and its connectors, for compatibility when
adding/optimizing agentic workflows. All paths relative to repo root.

## LLM runtime — credit-free by default

- **`config/runtime_policy.json` → `api_free: true`.** `scripts/llm_runtime.py` then makes `llm_available()`
  return False even if `ANTHROPIC_API_KEY` is set, forcing every LLM stage onto its **in-session skill route**.
- **`require_llm(skill, bundle_hint)`** — required stages exit with an actionable "run `/<skill>`" message
  instead of calling the API. **`optional_llm(skill)`** — optional enhancers return None (skip cleanly).
- **`SKILL_MAP`** maps API stages → skills + bundle dirs + optional flag (`triage`→`/triage`,
  `deep_analysis`→`/deep-analysis`, `coverage_sweep`→`/coverage-sweep`, `poc_validation`→`/poc-validation`;
  has a **`deep_pass` slot** that is *not yet wired to a skill* — the attach point).

**Compatibility implication:** any new agentic workflow must run as an **in-session skill with a
prepare→skill→write triplet** (deterministic bundle in, deterministic validator out) to stay credit-free and
auditable. An API-calling agent would violate `api_free` and the budget model.

## Agents — 34 specs in `agents/*.md`

- **Always-on Step-2 specialists (13):** reentrancy, access_control, arithmetic, oracle, flash_loan, logic,
  dos, snapshot, economic_attack, token_integration, behavioral_state_analysis, semantic_guard,
  protocol_context (context-only).
- **Conditional (4):** cross_chain, upgrade_storage, erc4626, transient_storage (gated on static.json flags).
- **Step-0 deep-analysis (5):** invariant_extractor, interaction_mapper, deep_trace_agent,
  backward_trace_agent, multi_tx_agent (now driven by the `/deep-analysis` skill).
- **Recon (2):** attacker_mindset (ITE surface scoring → `output/attack_surface.json`), supply_chain_check.
- **Synthesis/review (10):** compound_synthesis, report_synthesis, exploitability_modeler,
  duplicate_risk_agent, judge_simulator, severity_calibrator, runtime_poc_agent, impact_chain_escalation,
  reference_diff_agent, (+ protocol context).

Each agent spec is a markdown prompt with: **Role · Inputs** (`static.json`, `attack_surface.json`,
`protocol_invariants.json`, `promising_threads.jsonl`, `prompts/human_auditor_methodology.md`) · **Tools**
(`retriever.py`, `immunefi_retriever.py`, MCP) · **Output schema** (`output/findings_<agent>.json`) · **ITE
field** (intent/technique/evasion).

## Skills — 27 in `.claude/skills/<name>/SKILL.md`

- **Credit-free triplets:** `/deep-analysis` (Step 0), `/triage` (Step 4), `/coverage-sweep` (long tail),
  `/poc-validation` — each: `*_prepare.py` (bundle) → in-session skill (reason) → `*_write.py` (validate +
  finalize). This is the **template** for any new agentic stage.
- **Specialist-spawn skills:** `/ite-audit` (full pipeline) + per-family (`/reentrancy`, `/oracle`,
  `/access-control`, …).
- **Utility/routing:** `/confirm` (multi_pass), `/human-queue`, `/surface`, `/supply-chain`, `/kb-patterns`,
  `/immunefi`.

## MCP connectors — `.mcp.json` + `tools/*_mcp_server.py`

| Server | Type | Tools | Data |
|--------|------|-------|------|
| **kb-search** | FastMCP (local) | `search_findings`, `search_immunefi`, `get_primitives`, `get_primitive_compounds` | local `kb/chroma/` + `kb/attack_primitives.json` (incl. `PRIM-021` sibling-parity) |
| **onchain-context** | FastMCP (local wrapper) | `get_bytecode`, `get_storage`, `get_tx_history`, `simulate_tx`, `get_tvl`, `get_volume`, `query_subgraph`, `detect_anomaly`, `resolve_rpc` | QuickNode/Dune/Graph/Chainlist (lazy; degrade if keys absent) |
| **immunefi-audit-competitions** | HTTP | GitBook MCP | remote `reports.immunefi.com/~gitbook/mcp` |

**Compatibility:** kb-search is the **grounding connector** an agentic deep-pass would lean on (retrieve
precedents of a candidate's shape — the recall lever from the literature). onchain-context is the **verifier**
connector (`simulate_tx`/`get_storage` to *prove* a hypothesized value-flow), currently under-used at deep-pass.
All MCP servers degrade gracefully (non-fatal `{"error":...}`), so an agentic step must tolerate missing keys.

## Orchestration & budget — `config/agent_policy.json`

- **Modes:** `fast` (triage only) · `normal` (specialists + PoC≤3) · `deep` (full + unlimited PoC + judge;
  approval-gated). Active: `deep`.
- **Coverage gate (deterministic):** `require_manifest`, `require_minimal_pass_for_all_in_scope_items`,
  `deep_pass_attack_surface_score_min: 3`, `review_gate_blocks_unassigned/unexamined`, `clear_requires_evidence`.
- **Multi-pass confirm:** High=3 / Critical=5 passes, threshold 0.6 → below routes to human queue.
- **Specialist review:** `scripts/run_specialist_review.py` → exploitability → dup-risk → severity →
  runtime-PoC → judge → decision matrix.

## The deep-pass attach point (where new agentic recall plugs in)

`scripts/deep_pass_queue.py` (clusters `needs_deep_pass` items into 6 priority tiers) →
`scripts/deep_pass_ledger.py` (budget) → `prompts/deep_pass_packet.md` (reasoning spec) →
`output/deep_pass_queue.json`. `advisory_escalation_gate.py` re-routes high-risk advisory-lens hits on cleared
surfaces back to `needs_deep_pass`. **This pipeline exists but its reasoning is not yet an agentic skill** —
the SKILL_MAP `deep_pass` slot is empty. That empty slot + the existing queue/ledger/packet + the
prepare→skill→write template = a ready, low-risk integration surface for an agentic deep-pass.
