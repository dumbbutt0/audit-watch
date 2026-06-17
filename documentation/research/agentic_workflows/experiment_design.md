# Reproducible Bug-Hunting & Generalization Experiments

Designs the experiments that decide whether an agentic deep-pass actually generalizes — reusing the
Phase-12/13 harness so results are comparable and overfit-resistant. **Design only; no code this round.**

## Shared apparatus (already built — reuse, don't rebuild)

- **Train protocols:** Velodrome, Renzo, Wildcat (`audits/*-bench/`, source already inspected).
- **Holdout protocol:** EthereumCreditGuild (`audits/ecg-2023-12-holdout/`) — source **not** used to design
  anything; plus acquire 1–2 *new* uninspected holdouts per experiment to avoid burning ECG.
- **Anchor corpus:** the 16 strict-eval subjects (the 0-FP gate).
- **Answer keys + scorer:** `documentation/evals/promotion_benchmark/benchmark_answer_keys.json` +
  `score_generalization.py` (emits Training / **Holdout (primary)** / Generalization / Anchor Recall; FP via
  the anchor re-sweep).
- **Firewall discipline:** design on train+anchors → **freeze** → score holdout; never edit in response to
  holdout results.

## Experiment E1 — Agentic deep-pass vs the value_flow generalization wall (primary)

**Question:** can an agentic deep-pass recover wrong-value bugs the *deterministic* value_flow_v2 could not
(Holdout Recall 0%)?

- **Subject set:** the value-flow bugs in the benchmark (train: Velodrome H-02/H-03, Renzo H-02/H-08, Wildcat
  H-06; holdout: ECG H-04/M-13/M-24 — the *different* sub-shapes that defeated v2).
- **Treatment:** a deep-pass skill (prepare→skill→write triplet on the `deep_pass` SKILL_MAP slot) that, per
  high-surface candidate function, runs ground→trace-provenance→(verify)→decide (see `architecture_analysis.md`
  §A). Credit-free, in-session.
- **Controls:** (c0) deterministic value_flow_v2 alone (the Phase-13 result); (c1) deep-pass **without** KB
  grounding (ablate retrieval); (c2) deep-pass **without** on-chain verify (ablate `simulate_tx`).
- **Procedure:** build the skill + prompts using only **train** candidates + anchors → **freeze** → run on the
  ECG holdout + the anchor corpus.
- **Primary metric:** **Holdout Recall** on ECG's wrong-value bugs. **Gates:** 0 new high/medium on the 16
  anchor subjects (hallucination/FP gate); every agentic finding carries an evidence span.
- **Decision rule:** accept only if Holdout Recall > 0 **and** anchor FP = 0. A high training recall with 0
  holdout recall = the agent overfit the prompt (report honestly, same as v2).

## Experiment E2 — RAG-conditioned specialist recall (cheap)

**Question:** does injecting shape-specific KB precedents into a specialist (`logic`/`semantic_guard`) raise
recall without raising FP?
- **Treatment:** prepend `get_primitives` + top-k `search_findings` for the candidate's tag to the specialist
  prompt. **Control:** specialist without injection.
- **Metric:** holdout recall on the specialist's family bugs; anchor FP delta = 0. Cheap A/B; informs whether
  grounding alone (no deep-pass) moves the needle.

## Experiment E3 — Critic-gated clears (FP-safe recall)

**Question:** does an agentic critic that requires attacker-path disproof before a clear reduce *false clears*
(thereby surfacing more real bugs)?
- **Subject:** the Beanstalk-style "confident false clearance" miss class (documented in prior evals).
- **Metric:** false-clear rate on a labeled set; must not increase the human-queue volume beyond a budget.
- Note: measures *clear quality*, not recall directly — a precision-of-clearing experiment.

## Experiment E4 — Cost/latency normalization (mandatory wrapper on E1–E3)

Every recall number is reported **cost-normalized**: tokens/candidate, wall-clock/candidate, and
human-queue load. Under `api_free` the "cost" is in-session skill turns, not API $; still bounded by the
`agent_policy` mode budgets (fast/normal/deep). A recall gain that triples deep-pass turns may not be worth it.

## Reproducibility checklist (applied to every experiment)

- [ ] Train/holdout split declared up front; holdout source unread during design.
- [ ] Detector/skill **frozen** before holdout scoring; firewall noted in the results doc.
- [ ] `score_generalization.py` run before/after; five metrics reported, **Holdout Recall primary**.
- [ ] 0-anchor-FP gate on the 16 subjects; any new FP → tighten/drop (the liquidation_health-rebalance rule).
- [ ] Every agentic finding has an evidence span (+ PoC/sim where feasible) — no hallucinated recall.
- [ ] Raw per-protocol outputs saved under `promotion_benchmark/raw_results/`; commands logged.
- [ ] Credit-free: runs on the in-session skill route (no API in the hot path).
