# P270 — SETUP (Fresh Full-Path Rerun With Selector + Impact-First Triage)

**RESEARCH-ONLY · production-PATH proof, NOT authority.** Runs the full route on a fresh scored contest with BOTH new
selection fixes enabled (P267 selector + P269 impact-first triage), to test whether the system now recovers an awarded
mechanism end-to-end (exact/strong, PoC/runtime-supported).

## Full path
`P260 prioritizer → P262 recall sweep → P264 shadow harness → standalone advisory dashboard → P267 selector →
P269 impact-first triage → B/C ranking + five-op completion → full/partial-runtime PoC → pre-reveal gate → reveal`.

## Target
`code-423n4/2024-02-wise-lending` (EVM lending; liquidation/bad-debt/share-accounting/Pendle power-farm). Source-only
clone at `/tmp/p270_fresh/wise` (isolated, NEVER under `audits/`). Answer key `2024-02-wise-lending-findings` (PUBLIC,
sealed until Phase 9). Zero prior exposure; training-confound disclosed. See TARGET_SCREEN.md.

## Frozen modules (verified unchanged pre-run; must stay byte-identical — NO tuning)
| module | sha256[:16] |
|---|---|
| locus_shape_prioritizer.py (P260) | `d6b494bc3c0cc746` |
| recall_first_shape_sweep.py (P262) | `a48336275cb65a4f` |
| recall_first_harness.py (P264) | `85f9cbe662d2d991` |
| mechanism_pairwise_selector.py (P267) | `b0623b8c88752059` |
| impact_first_poc_triage.py (P269) | `63c88d02d2c7eefa` |
(+ configs: P260 `c61da091`, P262 `62e860199`, P264 `e9b74687`, P267 `9dab060d`, P269 `7c174b5d`.)

Forbidden 5 byte-identical: dashboard_sync `c1af70e1` · deep_trace `c095c426` · min_confirm_gate `2a15169a` ·
confirm_gate `afc481c9` · validate_p208 `ae55eb80`. Active audit `output → audits/size-credit-2024-06-blind/output`.

## Toolchain
foundry 1.5.1 + solc 0.8.24 (target pin). PoCs isolated under `pocs/p270/wise/`; deps cloned pinned (forge-std,
OZ v4.9.x) since the contest libs are npm-managed.

## Safety rails
No production authority / auto-submission / final severity / reportable / submission-ready / confirmed dashboard.
No frozen-module or PoC-layer tuning during the run. No production/contest source edits. Answer key sealed until the
full pre-reveal set is frozen+hashed. No answer-key content used to generate candidates or assign selector/triage
dimensions. Credit only pre-reveal outputs.
