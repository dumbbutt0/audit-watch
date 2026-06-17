# P131 — Run Setup & Method

## Goal
Answer P130's open question: does the candidate-stage boost (risk-tagged library/internal/helper logic →
deep-pass cutoff) **recover real recall** and **avoid inflating FP** (esp. `arithmetic`/`economic_attack`
speculative) downstream? Scope: a **focused A/B on the boost-delta candidates** on noya.

## Why not a literal full pipeline run (honest limits)
- **slither/static degraded:** noya has no remappings/node_modules; its `@openzeppelin/contracts-5.0` + Pendle
  imports won't compile, so `static_analysis.py` (slither) can't produce a real `static.json`. The candidate-
  stage manifest A/B is **regex-based and does not depend on slither**, so it is unaffected; downstream
  slither-driven signals (slither_hits/risk_score bonuses) are simply absent (degraded, noted).
- **Scale:** a 13-specialist sweep over noya's 377 in-scope functions in-session is intractable.
- **FP needs human verdicts:** a non-awarded confirmed finding can be valid-unawarded OR a FP; auto-labeling
  it FP would violate the P129 honesty rule. Such cases are routed to **needs_human_review**.

## What was run
1. **Deterministic A/B (Stage 1):** active→noya; regenerate the coverage manifest twice with identical
   `--contract` under noya's **real `scope.txt`** (40 in-scope files / 377 in-scope fns), toggling
   `coverage_policy.library_internal_surface_boost` OFF then ON, restoring it to its committed `true`. Outputs
   `noya_OFF.json` / `noya_ON.json`; boost-delta = items with `surface_boost == "library_internal_risk"`.
2. **Recall arm (Stage 2):** read the source of the awarded functions that the boost newly surfaces and assess
   discoverability (in-session specialist + ICE reasoning, grounded in source).
3. **FP arm (Stage 2):** categorize all 60 non-awarded boosted functions; read representatives (trivial getter,
   mock, on-class) to ground the FP-tendency estimate.
4. **Classify & decide (Stages 3-4):** recall delta vs the awarded yardstick; FP-tendency; decision.

## Honesty notes
- The specialist pass is an **in-session reviewer assessment grounded in source** (the API-free method),
  bounded to the recall arm (8 awarded fns, read in full) + a categorized scan of all 60 non-awarded boosted
  (representatives read). It is **not** the full automated 13-specialist + human-ground-truth stack.
- Recall is **objective** (deep-pass visibility vs the awarded yardstick). FP is an **estimate**; valid-
  unawarded findings → needs_human_review, never auto-labeled.
- The P130 repair code was **not changed**; config was toggled and **restored**. Active audit restored to
  `quantamm-2024-12-eval`.
