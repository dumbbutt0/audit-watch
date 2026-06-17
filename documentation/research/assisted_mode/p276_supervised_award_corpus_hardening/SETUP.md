# P276 — SETUP (SUPERVISED_EVAL)

Mode **SUPERVISED_EVAL**: award keys used for **scoring + failure localization only** — never to fabricate blind claims.
All outputs labeled `SUPERVISED_EVAL`. This phase **maps and proposes**; it edits **no** frozen module (repairs are a
later approved phase).

## Frozen baselines (byte-identical pre/post)
P260 `d6b494bc3c0cc746` · P262 `a48336275cb65a4f` · P264 harness `85f9cbe662d2d991` · P267 `b0623b8c88752059` ·
P269 `63c88d02d2c7eefa` · P273 `b87e3d22d1fb915b` + configs (`3fbc476e`/`7c174b5d`/`9dab060d`) + P271 checklist
`2929a2154a88104e`. Forbidden-5: dashboard_sync `c1af70e1` · deep_trace `c095c426` · min_confirm_gate `2a15169a` ·
confirm_gate `afc481c9` · validate_p208 `ae55eb80`. Active audit symlink → `audits/size-credit-2024-06-blind/output`.

## New additive glue (research-only, advisory, un-wired)
`scripts/research/p276_corpus_replay.py` (Pass A) · `scripts/research/p276_award_funnel_map.py` (Pass B + award-key
adapter) · `scripts/research/p276_metrics.py` (aggregator). None route/gate/set severity.

## Procedure
- **Pass A (no key):** per contest, from `audits/<id>/output/coverage_manifest.json` → regen checkpoints → frozen P264
  harness (shadow) → auto-built P273 coverage (class signals = locus name tokens) → auto-built P269 triage.
- **Pass B (key):** open the contest award key; map every awarded H/M to the furthest funnel stage + first_failed_stage.
