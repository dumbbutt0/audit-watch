# Implementation Roadmap — Agentic Workflows

Prioritized by **expected holdout-recall gain ÷ effort**, every item gated by the Phase-13 discipline
(Holdout Recall primary · 0 anchor FP · credit-free · evidence-anchored). Research/roadmap only — nothing
here is built or wired this round.

## Primary KPIs (governance)

| KPI | Definition | Current (after E1b) |
|-----|------------|--------------------|
| **Candidate Coverage Recall** (NEW headline — "did the agent get the chance?") | bugs whose fn enters the queue / all benchmark bugs | **8/9 = 89%** (routed-only was 5/9; ceiling 8/9 — `creditMultiplier` non-function) |
| Candidate Precision + Queue Size | covered / queue size (anti-noise guard) | ~1–2% per protocol (queues 64–207); reported so coverage isn't bought with noise |
| Coverage-by-source (provenance) | covered bugs reachable via detector vs semantic_surface | `{detector:5, semantic_surface:10}` — the 3 newly-covered bugs are surface-only |
| **Holdout Recall** (reasoning, primary) | agentic recoveries / family bugs on an *uninspected* protocol | DEFERRED to E1c (fresh `2024-03-abracadabra-money`; ECG reasoning contaminated) |
| Training Recall (reasoning) | recoveries / family bugs on inspected protocols | **6/6 = 100%** (E1 5/6 → recovered `_blockAccount` once surfaced) |
| Anchor FP rate | hallucinated findings | **0** |
| Holdout Exploit-Reproduction Recall | holdout recoveries carrying a correct REPRO_HINT | tracked (E1c) |

**E1b OUTCOME (executed):** built the semantic surface sampler (`config/semantic_surface_patterns.json` +
`deep_pass_prepare.py --surface-sample/--coverage-queue`) and the Candidate Coverage/Precision/provenance KPIs.
**Coverage 5/9 → 8/9**; the 3 router-missed bugs are now covered **via the sampler, not detectors**; reasoning
recovered the newly-surfaced Wildcat bug (**Training 6/6**), 0 hallucinated. Confirms the post-E1 reframing:
**the ceiling was coverage, not reasoning.** Docs: `surface_expansion_results.md`.

**E1c OUTCOME (executed) — fresh-holdout generalization on `2024-03-abracadabra-money` (frozen sampler, BLIND
reasoning):** Fresh Holdout Candidate Coverage Recall **2/5 = 40%**, Queue Size **79** (tolerable), Reasoning
Recall **1/5** (recovered C4 **M-10** `MagicLpAggregator._getReserves` missing-return → LP oracle = 0, **blind**),
Hint Quality **1/1**. **Verdict: PARTIAL generalization** — the queue is NOT just memorizing the benchmark (it
found a real awarded bug on an unseen protocol, blind, at a small queue), but coverage is **vocabulary-limited**
(misses `latestAnswer`/`buyShares` — sampler name-regex lacks oracle/price/buy terms). The gap is a
**coverage-SOURCE** problem, not reasoning or size. Docs: `fresh_holdout_results.md` + attestation E1c addendum.
**Next lever = sampler vocabulary breadth, validated on a 3rd fresh holdout (no tuning to Abracadabra)** — same
overfit discipline. Effort split unchanged: 50% surface/candidate-gen · 30% exploit-reproduction loop · 10%
benchmark · 10% detector maintenance.

**Phase-15 OUTCOME (executed) — Vocabulary Generalization (one variable: sampler vocab; config-only, e1b-v1→
e1d-v1):** added generic `oracle`/`aggregator`/trading-share vocab. Train gate PASS (queue ×1.11, precision
<10% loss). Contaminated Abracadabra 2/5→5/5 (oracle/buyShares) — **but** the **clean blind holdout #3
(LoopFi)** showed **ΔCoverage = 0**: all 7/13 covered family-shaped bugs were already reachable via baseline
categories; **0/7 came from the new vocab**, and blind Reasoning Recall = **0/13** (loopfi bugs are subtle
penalty/scale/conversion/excluded-term, already-covered). **Verdict: vocab NOT validated as a generalizer
(contaminated-only benefit); roll back `aggregator` (0 coverage anywhere); the real wall is REASONING DEPTH,
not vocabulary.** Single-variable proof: prepare/prompt/value_flow hashes unchanged. Docs:
`documentation/evals/vocabulary_generalization/` (6 files incl. `executive_summary.md`). Research-only/un-wired
(sampler `research_only:true`, e1d-v1 labeled experimental-unvalidated). **Next: a depth pass (trace into
callees / missing-term checks), measured on a fresh blind holdout — not more vocab.**

**Phase-16 OUTCOME (executed) — Reasoning-Depth Generalization (one variable: a NEW depth-trace prompt
`prompts/deep_pass_depth_trace.md`; baseline prompt + sampler + scripts byte-frozen = single-variable proof):**
generic depth checklist (formula reconstruction · missing fee/penalty/scale/profit term · unit/basis · callee
trace · two-sided evidence · mandatory "no finding" path). Blind A/B on fresh holdout #4 = `2024-05-bakerfi`
(leveraged vault; NOT PoolTogether — contamination): **Baseline Reasoning Recall 0/7 → Reasoning-Depth Recall
2/7**, **2 depth-only blind recoveries** (BakerFi M-21+M-36 — `harvest` excludes P&L/flashloan-fee when
`deltaDebt>0`), **0 hallucination increase** (0→0), coverage 6/7. Win came from **formula/missing-term**
analysis (internal-callee tracing contributed 0 here). **VERDICT: STRONG SUCCESS** (cleared the bar on ONE holdout) → recommended re-validation before promotion.
Docs: `documentation/evals/reasoning_depth/` (7 files). Research-only.

**Phase-17 OUTCOME (executed) — Depth Replication Battery (depth_trace_v1 FROZEN `ab3a57ca`, verified
unchanged start→end; 3 fresh blind holdouts):** DittoETH (lending), Spectra (vault/yield), KelpDAO (oracle/
scale). **RESULT = FAILURE — the BakerFi win did NOT generalize:** 0 depth recoveries across the 3 holdouts and
**+2 hallucinations** on Kelp (depth flagged a latent non-exploitable `scale_mismatch` on getRsETHAmountToMint/
getRSETHPrice while MISSING the real order-of-operations H-62 + first-staker H-42 bugs on those same functions).
Coverage was fine (4/5 in-queue) → this is a **reasoning-generalization failure, not a sampler failure**.
internal-callee + conversion classes contributed **0 real recoveries across all 4 holdouts**; only excluded-term
(BakerFi) ever worked. **The Phase-16 "promote" recommendation is OVERTURNED → REVISE AND RETEST, do NOT
promote** (add an "exploitable-as-deployed" gate to kill latent over-flags; actually apply the order-of-ops
step). Docs: `documentation/evals/reasoning_depth_replication/` (9 files). Research-only; 946 tests pass.

**Phase-18 OUTCOME (executed) — Depth Failure Repair (NEW prompt depth_trace_v2 `bd931f06`; v1 + all artifacts
frozen-unchanged):** v2 adds exploitable-as-deployed + mechanism-match gates + order-of-ops + first-actor +
scale-skepticism. Contaminated regression: v2 **rejects the Kelp latent-scale hallucination** (v1's +2) and
keeps BakerFi excluded-term. Fresh blind A/B/C (Basin `2024-07`, Salty `2024-01`): **baseline 0 / v1 0 / v2 0
recoveries, 0 hallucinations**; v2 +3 explicit latent-rejections. **VERDICT = PARTIAL: v2 is strictly SAFER
than v1 (fixes the latent-scale hallucination class at zero recall cost) but recovers NO new blind bug.** v2's
order-of-ops/first-actor gates **did not convert** even on Salty's in-queue H-312/H-614/H-137 → binding wall is
**reasoning DEPTH/COVERAGE over large queues**, not prompt design. **Rec: ADOPT v2 over v1 as the experimental
prompt; keep depth pass OFF/experimental; do NOT promote. Next lever is NOT depth_trace_v3 — it is exhaustive
per-candidate/per-callee tracing or accepting a recall ceiling.** Docs: `documentation/evals/reasoning_depth_v2/`
(10 files). Research-only; 948 tests pass.

**Phase-19 OUTCOME (executed) — Reasoning Coverage Program (instrumentation + scheduler; NO prompt/detector/
sampler edits, all frozen-unchanged):** measured trace coverage on Salty/Basin. **PROVES the coverage
hypothesis:** Candidate Coverage Recall 5/7 vs **Reasoning Coverage Recall 2/7** (3 bug fns queued-but-never-
read); only **21% of candidates body-read**; Deep-Trace Coverage **12%**; Callee Trace **40%**. Miss-attribution
(7 bugs): **5/7 = COVERAGE failures** (queued_but_not_read 3 + read_but_callees_missed 2), 1 sampler, **1 true
reasoning failure**. Recovered-vs-Missed chart: Recovered **100%** body-read vs Missed **29% on large queues**
(80% on BakerFi's small fully-read queue → reasoning binds only AFTER coverage is high). Built
**`scripts/deep_pass_schedule.py`** (research-only/un-wired): one-candidate-per-bundle + mandatory recursive
callee expansion + budget + resumable trace-ledger + untraced reporting (demo Salty 59: budgeted+resumable;
a candidate is 'traced' only when callee-complete). **Rec: ADOPT the scheduler as the experimental deep-pass
front-end; the binding lever is exhaustive trace COVERAGE, not a depth_trace_v3.** Docs:
`documentation/evals/reasoning_coverage/` (6 files). Research-only; 950 tests pass.

## E1 OUTCOME (Phase-14, executed) — item #1 below

**Built + measured** the agentic deep-pass (wired the empty `deep_pass` SKILL_MAP slot;
`deep_pass_prepare.py` → `/deep-pass` → `deep_pass_write.py --eval`). Result:
`documentation/evals/promotion_benchmark/agentic_deep_pass_results.md` (+ `holdout_firewall_attestation.md`).
**Training 50%→83%** (reasoning, not packaging/KB — 4-rung ladder); **Holdout 0/3** because the deterministic
lenses route **0** candidates on ECG's wrong-value bugs (the deep-pass never sees them). **Refines** the
Phase-13 diagnosis: reasoning works on routed candidates; the holdout wall is **routing recall**. No promotion
(stays research-only). **Next = E1b:** widen the deep-pass surface beyond detector-routed (bounded
high-surface/value-tag queue) so un-routed holdout bugs get a fair shot — same firewall, fresh holdout.

## Roadmap

| # | Item | Type | Expected gain | Effort | Risk | Gate |
|---|------|------|---------------|--------|------|------|
| **1** | **Agentic deep-pass skill** (E1) — wire the empty `deep_pass` SKILL_MAP slot: `deep_pass_prepare.py` (candidate bundles from `deep_pass_queue.json`) → `/deep-pass` skill (ground→trace-provenance→verify→decide) → `deep_pass_write.py` | NEW credit-free triplet | **highest** — directly targets the wrong-value/semantic recall wall | Med | hallucinated findings | Holdout Recall > 0 **and** 0 anchor FP, frozen-before-holdout |
| **2** | **RAG-conditioned specialists** (E2) — inject shape-specific `get_primitives`/`search_findings` into `logic`/`semantic_guard` prompts | prompt change | medium, cheap | Low | mild FP | holdout recall ↑, anchor FP Δ=0 |
| **3** | **Critic-gated clears** (E3) — agentic attacker-path-disproof before any clear (no-silent-clear as reasoning) | skill sub-step | medium (fewer false clears) | Low-Med | queue inflation | false-clear rate ↓, queue within budget |
| **4** | **On-chain verifier in deep-pass** — use `simulate_tx`/`get_storage` to turn a hypothesized value-flow into a proof | connector wiring | medium (precision) | Med | key-absent degradation | proof attached or finding demoted |
| **5** | **Deep-pass graph orchestration** (router→specialist→critic→judge) | refactor | structural, after #1 validated | Med | over-engineering | no metric regression |
| 6 | Tree/Graph-of-Thought for High/Critical only | depth lever | low breadth | Med-High | cost | reserved to `deep` mode budget |

## Sequencing

1. **Build #1 (agentic deep-pass) on the train protocols + anchors, freeze, score on the ECG holdout.** This
   is the single experiment that answers "does agentic reasoning cross the generalization wall the
   deterministic detectors hit?" If Holdout Recall > 0 at 0 anchor FP → the strategy works; iterate (#2/#4).
   If Holdout Recall = 0 → honest negative (the agent overfit the prompt), and the bottleneck is deeper
   (model capability / verification), not workflow — re-rank.
2. **#2 + #3 are cheap parallel A/Bs** that inform #1's prompt without much risk.
3. **#4 → #5** only after #1 shows holdout signal.

## Constraints carried from the platform

- **Credit-free:** all of the above run on the in-session skill route; no API in the hot path (`api_free=true`).
- **Research-only / un-wired first:** like the detectors, an agentic deep-pass ships research-only (no routing
  into the production gate) until it clears a holdout bar; promotion is a separate human decision.
- **Determinism at the seams:** the prepare/write halves stay deterministic + validated; only the middle
  (the skill) is the LLM step — preserving auditability and the coverage gates.

## The honest framing for stakeholders

Phase 13 showed deterministic detectors plateau at the *family* boundary. Agentic reasoning is the credible
next lever **and** the most overfit-prone one. This roadmap treats it the same way the detector work was
treated: **build small, freeze, measure on a holdout, report the primary number honestly.** The first
deliverable's success is not "it found the demo bugs" — it's **Holdout Recall on a protocol nobody designed
it against.**
