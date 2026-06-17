# P268 — SETUP (Fresh Full-Path Test With Pairwise Selector)

**RESEARCH-ONLY · production-PATH test, NOT production authority.** Re-runs the P266 full operational route on a
FRESH scored contest with the **P267 pairwise selector inserted between B/C ranking and completion/PoC**, to measure
whether preserving the high-impact top-2 mechanism converts into EXACT/STRONG mechanism recovery.

## Architecture under test (P267 is the only new stage vs P266)
`P260 prioritizer → P262 recall sweep → P264 shadow harness / advisory dashboard → triage → B/C top-2 ranking →
**P267 pairwise selector** → five-op completion (both on KEEP_BOTH) → PoC queue → Foundry PoC → pre-reveal gate →
reveal + exact-mechanism scoring`.

## Target
`code-423n4/2024-07-karak` (Karak restaking — Vault/Core/NativeVault + slashing/withdrawals). Source-only clone at
`/tmp/p268_fresh/karak` (isolated, NOT under `audits/`). Answer key `code-423n4/2024-07-karak-findings` (PUBLIC,
sealed until Phase 11). Zero prior repo exposure; training-confound disclosed. See TARGET_SCREEN.md.

## Frozen inputs (verified unchanged pre-run; must stay byte-identical — NO tuning)
| module | sha256[:16] |
|---|---|
| locus_shape_prioritizer.py (P260) | `d6b494bc3c0cc746` |
| recall_first_shape_sweep.py (P262) | `a48336275cb65a4f` |
| recall_first_harness.py (P264) | `85f9cbe662d2d991` |
| **mechanism_pairwise_selector.py (P267)** | `b0623b8c88752059` |
(+ their configs: P260 `c61da091`, P262 `62e860199`, P264 `e9b74687`, P267 `9dab060d`.)

Forbidden 5 byte-identical: dashboard_sync `c1af70e1` · deep_trace `c095c426` · min_confirm_gate `2a15169a` ·
confirm_gate `afc481c9` · validate_p208 `ae55eb80`. Active audit `output → audits/size-credit-2024-06-blind/output`
(unchanged; no `switch_audit`).

## Checkpoints + manifest
Built isolated under the P268 `outputs/` dir from the karak source via the deterministic, unchanged scripts
`build_coverage_manifest.py` (scope.txt-aware), `accounting_checkpoint_audit.py`, `state_transition_checkpoint_audit.py`.

## Safety rails
No production authority / auto-submission / final severity / reportable / submission-ready. Dashboard advisory-only
(standalone; no dashboard.py/dashboard_sync.py/canonical touch). Answer key sealed until the full pre-reveal set
(harness, advisory feed, ranking, selector, completion, PoC-intent, gate) is frozen + hashed. No answer-key content
used to generate candidates or assign selector dimensions. Fresh source isolated in `/tmp`; PoCs under `pocs/p268/`.
