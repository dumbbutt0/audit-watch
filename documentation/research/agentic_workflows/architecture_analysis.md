# Agentic Architecture Analysis & Optimization Strategies

Analyzes the existing Audit-Watch agentic architecture, where it is strong/weak, and the optimization
strategies that fit — judged against the **Phase-13 constraint** (the open frontier is *recall* on bugs the
deterministic lenses can't generalize to, measured on a holdout, at 0 anchor FP, under `api_free`).

## Current architecture (as-is)

```
Step 0.25  attacker_mindset  → attack_surface.json (router signal)
Step 0     /deep-analysis    → invariants → interactions → traces (plan-execute)
Step 1     static + supply-chain
Step 2     /ite-audit        → 13+ specialist agents (parallel ensemble) → findings_<agent>.json
           /coverage-sweep   → long-tail dispositions (evidence-gated)
   (research-only, parallel)  20 deterministic recall lenses → *_audit.json   ← Phase-13 wall here
Step 2.5–3 cross-agent merge → compound_synthesis (CC-###)
Step 3.5   /confirm          → multi-pass (3–5) ensemble
Step 3.9   coverage + min-confirm gate (deterministic, hard-block)
Step 4     /triage           → ICE re-derive; no-silent-clear → human queue
Step 5     run_specialist_review → exploitability/dup/severity/PoC/judge → decision matrix
deep-pass  deep_pass_queue → ledger → packet  ← reasoning NOT yet agentic (empty SKILL_MAP slot)
```

**Strengths:** strong FP-suppression (judge, multi-pass, no-silent-clear, evidence-gated clears); a clean
**prepare→skill→write** credit-free pattern; deterministic coverage gates; rich grounding connectors
(kb-search, onchain-context). **Weakness (Phase-13):** *recall* on semantic/wrong-value bugs — the
deterministic lenses overfit their anchors; the agentic specialists are broad (per-vuln-class) and don't
do focused per-candidate value-provenance reasoning.

## Optimization strategies, ranked by fit

### A. Agentic deep-pass over detector candidates (highest fit) — "verify-and-extend the lens output"
The deterministic lenses already *route* the right functions (recall-first) but miss the *isolation* and the
generalizable wrong-value shapes. An agentic deep-pass that takes each `needs_deep_pass`/high-surface
candidate and runs a **ReAct + RAG + on-chain-verify** loop is the literature's recall lever applied exactly
where the gap is:
1. **Ground** — `kb-search.get_primitives`/`search_findings` for precedents of the candidate's shape.
2. **Trace value provenance** — read the function + 1–2 callees (reuse `_function_body`), identify each
   value's origin and the consumer that acts on it; flag where the wrong variable/key/index/identity feeds a
   check or effect (the generalized wrong-value reasoning the deterministic shapes can't enumerate).
3. **Verify** — optionally `simulate_tx`/`get_storage` to confirm reachability/state (turns assertion → proof).
4. **Decide** — `finding | strong-clear (attacker_reachability+guard+no_impact) | needs_human` — never silent clear.
Plugs into the **existing `deep_pass_queue`/`ledger`/`packet`** via a new prepare→skill→write triplet; the
SKILL_MAP `deep_pass` slot is already reserved.

### B. RAG-conditioned specialists (medium fit) — cheap recall boost, low risk
Inject *shape-specific* retrieved precedents into the relevant specialist prompt (e.g., feed the
wrong-value/registry-lifecycle primitives + 2–3 nearest KB findings into `logic.md`/`semantic_guard.md`).
The connectors exist (`get_primitives`, `search_findings`); this is prompt-level, no new orchestration.

### C. Critic/verifier loop on clears (medium fit) — FP-safe recall
A critic sub-step that, before any agentic "clear", demands a concrete attacker-path *disproof* (the
no-silent-clear rule made agentic). Turns the existing rule from a write-time check into a reasoning step.
Improves the *quality* of clears (fewer false clears = more real bugs surfaced) without raising FP.

### D. Graph orchestration of the deep-pass (medium fit, later) — router → specialist → critic → judge
Wrap (A)+(C) in a small typed graph (LangGraph-style, but implemented as the prepare→skill→write triplet so
it stays credit-free + deterministic at the seams). Adds structure once (A) is validated; not first.

### E. Tree/Graph-of-Thought per candidate (low fit now) — high cost
Reserve branch-exploration for confirmed High/Critical candidates only (budget under `deep` mode); not a
generalization lever, a depth lever.

## Anti-patterns to avoid (Phase-13 lessons applied to agents)
- **Demo-driven acceptance.** An agentic deep-pass that "recovers Velodrome M-10 + the Renzo bugs" in a demo
  is *training recall* — it must be re-measured on an **uninspected holdout** (Holdout Recall primary) before
  any claim of generalization. Agents overfit prompts the way detectors overfit vocab.
- **Hallucinated recall.** LLM "findings" without an evidence span / verifier are FPs. Gate every agentic
  finding with an evidence span + (where feasible) a `simulate_tx`/PoC, and the same **0-anchor-FP** check on
  the 16-subject corpus that the deterministic shapes pass.
- **Credit creep.** Stay on the in-session skill route (`api_free`); no API-calling agents in the hot path.

## Where the architecture should evolve
Keep the deterministic lenses as the **recall-first router** (they're cheap and FP-clean), and add **one
agentic deep-pass** as the *precision+generalization* second stage over their high-surface output — measured
on the train/holdout benchmark. That is the minimal, highest-leverage change, and it uses infrastructure that
already exists.
