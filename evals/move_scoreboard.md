# Recall Lab — Move Scoreboard

_generated 2026-06-18T00:31:11Z_

Eval-only, move-only. NEVER counted toward Solidity recall (the Solidity board routes these out). The honest non-Solidity recall number lives here.

## Headline
- **Recall — FULL-COVERAGE only (honest):** 1.0  (over 7 awarded findings in full-coverage cold passes)
- Recall — of-surfaced (may include thin passes): 1.0  (strong-only 1.0)
- Misses: 0 coverage-gap / 0 reasoning-gap · pending 0

| project | recall | strong | awarded | coverage | full? |
|---|---|---|---|---|---|
| sui-amm-swap-2022-11-eval | 1.0 | 1.0 | 7 | 100% | ✅ |

## Per-mechanism-class recall

| mechanism class | recall | strong | n | missed | status | prompt § |
|---|---|---|---|---|---|---|
| move-capability-safety | 1.0 | 1.0 | 1 | 0 | seeded | move_object_capability.md |
| move-constant-product-invariant-recheck | 1.0 | 1.0 | 1 | 0 | reincorporated | move_clmm_math.md#7 |
| move-empty-vector-input-validation | 1.0 | 1.0 | 1 | 0 | untagged | - |
| move-first-deposit-liquidity-lock | 1.0 | 1.0 | 1 | 0 | untagged | - |
| move-public-helper-visibility | 1.0 | 1.0 | 1 | 0 | reincorporated | move_object_capability.md#7 |
| move-rounding-direction | 1.0 | 1.0 | 1 | 0 | seeded | move_clmm_math.md |
| move-zero-share-deposit-fundloss | 1.0 | 1.0 | 1 | 0 | untagged | - |

## Non-blind reincorporations — NON-BLIND, not banked as blind recall

> These classes were reincorporated from a **NON-BLIND** / source-level eval (the auditor saw the report; there is no blind cold-pass fixture/adjudication on disk). They are honestly **not banked** toward the blind-recall headline above — provenance only.

| eval (non-blind) | classes reincorporated |
|---|---|
| secret-vault-aptos-2025-07-blind | move-address-param-not-signer-auth, move-onchain-data-not-private |
