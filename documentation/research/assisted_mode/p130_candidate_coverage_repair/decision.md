# P130 — Decision

## Decision: **ACCEPT_WITH_LIMITS**

A small, general source-resolution repair (contract-type tagging + a two-signal, per-contract-capped,
config-reversible boost of risk-tagged library/internal/helper logic to the deep-pass cutoff) **materially
improves candidate-stage coverage of the exact miss class P129 measured** — risk-bearing library/facet/helper
logic that was enumerated and in-scope but ranked below the cutoff — **without any precision-metric
regression**. It is accepted **with limits** because the deep-pass volume increase on library-heavy audits
(+44% on noya) is a real reviewer-cost / latent-FP risk whose downstream effect is **unverified** (needs a
full pipeline run).

### Why not the other labels
- **Not REJECT_OVERFIT:** the repair keys only on generic structure (`contract_type`, visibility, mutability,
  `Facet` suffix) and the *existing* risk-tag bucket — no contract names, issue ids, or answer-key paths. It
  was developed and measured on noya/decent (Beanstalk source was absent), and it lifted a **non-motivating**
  audit's awarded-function coverage by +42 pp while barely touching a non-library control. By construction it
  cannot be Beanstalk-overfit.
- **Not REJECT_NO_GAIN:** noya awarded-FUNCTION coverage 32% → 74%; internal-fn ≥3 1% → 6%; awarded-contract
  89% → 95%.
- **Not unconditional ACCEPT_REPAIR:** +44% deep-pass inflation on library-heavy audits and the unverified
  downstream FP impact warrant the cap + flag gating and a confirming pipeline run before defaulting on for
  production submission audits.

### Limits / conditions of acceptance
1. Keep the per-contract cap (default 3) and the two-signal gate; both are tunable via
   `config/agent_policy.json` without code change.
2. Keep `library_internal_surface_boost` flag-gated (one flip = exact prior behavior).
3. Before relying on it for a real submission audit, run the full pipeline on a library-heavy audit and
   confirm the +44% deep-pass set does **not** inflate `arithmetic`/`economic_attack` speculative FPs beyond
   the P129 FP rate (0.143).

## Final answer
- **What changed:** `build_coverage_manifest.py` now tags each item's `contract_type` and lifts risk-tagged
  computation/helper logic (internal/private OR view/pure OR library OR `*Facet`, AND a tag in
  {accounting,token,oracle,migration,config}) to the deep-pass cutoff — two-signal, capped at 3/contract,
  config-reversible. (+ config flags, + 10 tests.)
- **Why general:** keys only on architecture-level structure + the existing risk-tag bucket; no protocol/
  answer-key strings; developed without Beanstalk source; effect scales with library density (large on noya,
  ~nil on decent).
- **Before/after recall (candidate-coverage proxy):** noya awarded-FUNCTION coverage **32% → 74% (+42 pp)**;
  awarded-CONTRACT 89% → 95%; internal-fn ≥3 1% → 6%. decent (control) unchanged.
- **Before/after correct-contract miss count:** noya uncovered awarded functions 13 → 5 (of 19); Beanstalk
  taxonomy shows 87% of its 38 misses are source-resolution, 68% in the class this repair targets.
- **FP / runtime impact:** precision metrics invariant (FP 0.143, over-severity 0.267); deep-pass volume
  +44% (noya) / +13% (decent), capped; tool runtime unchanged; downstream FP unverified (pipeline run needed).
- **Tests run:** 10 new (all pass); full suite 1572 passed / 2 pre-existing snapshot fails / 4 skipped;
  determinism + research self-test OK; no severity/submission/detector files touched.
- **Holdout result:** repair fires proportional to architecture — big on noya (library-heavy), minimal on
  decent (no libraries); no broken paths, no new failures.
- **Decision:** ACCEPT_WITH_LIMITS.
- **Next recommended phase (P131):** run the full pipeline on a library-heavy audit (e.g. noya) end-to-end to
  measure the repair's true downstream recall **and** FP impact; then address the residual non-ranking
  classes — `(absent)` functions (enumeration/scope-membership) and `proxy_or_facet_alias_failure` (Diamond
  selector→facet resolution) — and consider promoting callgraph-reachability boosting over the tag+shape proxy.
