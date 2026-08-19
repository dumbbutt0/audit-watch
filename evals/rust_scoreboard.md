# Recall Lab — Rust Scoreboard

_generated 2026-07-06T16:02:31Z_

Eval-only, rust-only. NEVER counted toward Solidity recall (the Solidity board routes these out). The honest non-Solidity recall number lives here.

## Headline
- **Recall — FULL-COVERAGE only (honest):** 0.8  (over 5 awarded findings in full-coverage cold passes)
- Recall — of-surfaced (may include thin passes): 0.4  (strong-only 0.4)
- Misses: 0 coverage-gap / 6 reasoning-gap · pending 0

| project | recall | strong | awarded | coverage | full? |
|---|---|---|---|---|---|
| orderly-solana-2024-10-eval | 0.667 | 0.667 | 3 | 100% | ✅ |
| pyth-lazer-solana-2024-eval | 1.0 | 1.0 | 2 | 100% | ✅ |
| woofi-solana-2024-08-eval | 0.0 | 0.0 | 5 | 41% | thin |

## Per-mechanism-class recall

| mechanism class | recall | strong | n | missed | status | prompt § |
|---|---|---|---|---|---|---|
| lz-ordered-execution-option-missing | 0.0 | 0.0 | 1 | 1 | reincorporated | solana_cpi.md |
| solana-duplicate-mutable-account-serialization | 0.0 | 0.0 | 1 | 1 | reincorporated | solana_account_model.md |
| solana-init-authority-mismatch-vs-use | 0.0 | 0.0 | 1 | 1 | reincorporated | solana_account_model.md |
| solana-missing-signer-check | 0.0 | 0.0 | 1 | 1 | reincorporated | solana_account_model.md |
| solana-pda-signer-seeds-missing-bump | 0.0 | 0.0 | 1 | 1 | reincorporated | solana_cpi.md |
| solana-missing-anchor-constraint | 0.667 | 0.667 | 3 | 1 | reincorporated | solana_account_model.md |
| solana-ed25519-introspection-data-unbound | 1.0 | 1.0 | 1 | 0 | reincorporated | solana_cpi.md |
| solana-reinit-missing-init-guard | 1.0 | 1.0 | 1 | 0 | reincorporated | solana_account_model.md |

## Non-blind reincorporations — NON-BLIND, not banked as blind recall

> These classes were reincorporated from a **NON-BLIND** / source-level eval (the auditor saw the report; there is no blind cold-pass fixture/adjudication on disk). They are honestly **not banked** toward the blind-recall headline above — provenance only.

| eval (non-blind) | classes reincorporated |
|---|---|
| drift-zellic-2022 | solana-anchor-idl-instructions-enabled, solana-arithmetic-unchecked |
| lz-solana-endpoint-zellic-2024 | solana-account-count-config-mismatch-panic, solana-account-substitution-confusion, solana-close-account-revival, solana-remaining-accounts-trust |
| pump-science-2025-01-blind | solana-lamport-invariant-includes-rent |
