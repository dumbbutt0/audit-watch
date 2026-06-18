# Recall Lab — Scoreboard

_generated 2026-06-18T03:07:42Z_

Eval-only. Does not affect the real-world dashboard.

## Headline
- **Holdout recall — FULL-COVERAGE only (the honest number):** 0.426  (over 94 awarded findings in full-coverage projects)
- Holdout recall — of-surfaced (may include thin passes): 0.441  (strong-only 0.186)
- **Training recall — FULL-COVERAGE only:** None  (over 0 findings); of-surfaced: 0.303 — regression set, contamination acknowledged

> Honest-score policy: only cold passes that examined EVERY substantive in-scope file count toward the full-coverage headline. Thin passes inflate recall_of_surfaced by hiding coverage-gap misses, so they are shown but excluded from the honest number. Per-project coverage% is in the tables below.

## Holdout  (recall 0.441, strong 0.186, misses: 1 coverage-gap / 56 reasoning-gap, pending 0)

| project | recall | strong | awarded | coverage | full? | note |
|---|---|---|---|---|---|---|
| chainlink-2026-03-blind | — | — | — | — | — | unscoreable: report kept private by C4 — unscoreable until a public awarded list exists |
| eggstravaganza-2025-04-blind | — | — | — | — | — | unscoreable |
| fluid-dex-v2-2026-02-blind | — | — | — | — | — | unscoreable: UNSCOREABLE: 12-file operate/supply sub-scope; sole in-scope finding H-1 excluded (title glimpsed prior setup) though caught STRONG blind (F-01); awarded M-1/M-2/M-3 are out-of-subscope (liquidate/DexV2). |
| garden-2025-11-blind | 0.0 | 0.0 | 1 | 100% | ✅ | heuristic (auto-detected, unconfirmed) |
| init-capital-2024-01-blind | 0.571 | 0.143 | 7 | 100% | ✅ |  |
| intuition-2026-03-blind | 1.0 | 0.5 | 2 | 0% | thin |  |
| iq-ai-2025-01-blind | 0.75 | 0.25 | 4 | 100% | ✅ |  |
| monetrix-2026-04-blind | 1.0 | 0.0 | 1 | 0% | thin |  |
| neobase-2024-03-blind | 0.375 | 0.125 | 8 | 100% | ✅ |  |
| next-generation-2025-01-blind | 0.5 | 0.25 | 4 | 100% | ✅ | heuristic (auto-detected, unconfirmed) |
| nudgexyz-2025-03-blind | 0.5 | 0.0 | 4 | 100% | ✅ |  |
| particle-2023-12-blind | 0.158 | 0.053 | 19 | 100% | ✅ |  |
| phi-2024-08-blind | 0.4 | 0.133 | 15 | 100% | ✅ |  |
| pizza-drop-aptos-2025-08-blind | — | — | — | — | — | unscoreable |
| pump-science-2025-01-blind | 0.4 | 0.4 | 5 | 25% | thin | heuristic (auto-detected, unconfirmed) |
| rustfund-2025-03-blind | 1.0 | 0.571 | 7 | 100% | ✅ | heuristic (auto-detected, unconfirmed) |
| secondswap-2024-12-blind | 0.304 | 0.13 | 23 | 100% | ✅ |  |
| secret-vault-aptos-2025-07-blind | 1.0 | 0.667 | 3 | 100% | ✅ | heuristic (auto-detected, unconfirmed) |
| traitforge-2024-07-blind | 0.24 | 0.0 | 25 | 100% | ✅ | heuristic (auto-detected, unconfirmed) |

## Training  (recall 0.303, strong 0.091, misses: 31 coverage-gap / 15 reasoning-gap, pending 0)

| project | recall | strong | awarded | coverage | full? | note |
|---|---|---|---|---|---|---|
| badger-2024-06-holdout | 0.0 | 0.0 | 2 | 0% | thin |  |
| beanstalk-2024-05 | 1.0 | 0.0 | 12 | 0% | thin | heuristic (auto-detected, unconfirmed) |
| cap-2025-07-eval | 0.4 | 0.1 | 10 | 56% | thin |  |
| centrifuge-2023-09-holdout | 0.0 | 0.0 | 9 | 0% | thin | heuristic (auto-detected, unconfirmed) |
| decent-2024-01-holdout | 0.222 | 0.0 | 9 | 0% | thin | heuristic (auto-detected, unconfirmed) |
| kleidi-2024-10-holdout | 0.333 | 0.0 | 3 | 0% | thin |  |
| munchables-2024-05-holdout | 1.0 | 0.333 | 6 | 0% | thin |  |
| numa-2024-12-eval | 0.0 | 0.0 | 16 | 9% | thin |  |
| olas-2026-01-blind | 0.174 | 0.0 | 23 | 1% | thin |  |
| pooltogether-2024-03-holdout | 0.111 | 0.0 | 9 | 0% | thin | heuristic (auto-detected, unconfirmed) |
| predy-2024-05-holdout | 0.083 | 0.0 | 12 | 0% | thin | heuristic (auto-detected, unconfirmed) |
| pyth-lazer-solana-2024-eval | — | — | — | — | — | rust (see evals/rust_scoreboard.md) |
| sui-amm-swap-2022-11-eval | — | — | — | — | — | move (see evals/move_scoreboard.md) |
| vultisig-2024-06-holdout | 0.833 | 0.5 | 6 | 0% | thin |  |
| zetachain-2023-10-holdout | 0.0 | 0.0 | 48 | 0% | thin | heuristic (auto-detected, unconfirmed) |

## Auto-detected misses (heuristic; incl. already-evaluated contests) — 162 total

> Advisory miss-detection over every contest with a cold pass + an answer key (any format). Heuristic + confidence-tagged; NOT part of the confirmed headline and NOT protected by the regression gate. Use to find unexamined expert-bug families to reincorporate.

| project | awarded | misses detected | heuristic recall |
|---|---|---|---|
| zetachain-2023-10-holdout | 48 | 48 | 0.0 |
| panoptic-2025-12-strict-eval | 22 | 19 | 0.136 |
| traitforge-2024-07-blind | 25 | 19 | 0.24 |
| revert-lend-2024-03-strict-eval | 31 | 18 | 0.419 |
| predy-2024-05-holdout | 12 | 11 | 0.083 |
| hybra-finance-2025-10-strict-eval | 10 | 10 | 0.0 |
| centrifuge-2023-09-holdout | 9 | 9 | 0.0 |
| pooltogether-2024-03-holdout | 9 | 8 | 0.111 |
| decent-2024-01-holdout | 9 | 7 | 0.222 |
| pump-science-2025-01-blind | 5 | 5 | 0.4 |
| rustfund-2025-03-blind | 7 | 4 | 1.0 |
| next-generation-2025-01-blind | 4 | 3 | 0.5 |
| garden-2025-11-blind | 1 | 1 | 0.0 |
| beanstalk-2024-05 | 12 | 0 | 1.0 |
| secret-vault-aptos-2025-07-blind | 3 | 0 | 1.0 |
| silo-finance-2025-03-strict-eval | 6 | 0 | 1.0 |

## Per-mechanism-class recall  (which expert-bug families we miss)

| mechanism class | recall | strong | n | missed | status | prompt § |
|---|---|---|---|---|---|---|
| aa-wallet-cross-chain-address | 0.0 | 0.0 | 1 | 1 | reincorporated | cross_chain.md |
| accrual-before-transfer | 0.0 | 0.0 | 1 | 1 | untagged | - |
| addpremium-no-fee-collect | 0.0 | 0.0 | 1 | 1 | untagged | - |
| baseamount-rounding-zero | 0.0 | 0.0 | 1 | 1 | untagged | - |
| blacklist-stuck-liquidity | 0.0 | 0.0 | 1 | 1 | untagged | - |
| bps-sqrt-precision-loss | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| bridge-refund-verification | 0.0 | 0.0 | 1 | 1 | untagged | - |
| burnable-token-design | 0.0 | 0.0 | 1 | 1 | design | - |
| buyback-grief | 0.0 | 0.0 | 1 | 1 | untagged | - |
| cached-config-not-refetched | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md#40 |
| cf-bypass-mint | 0.0 | 0.0 | 1 | 1 | untagged | - |
| close-liquidity-shortfall | 0.0 | 0.0 | 1 | 1 | untagged | - |
| collect-no-recipient-blacklist | 0.0 | 0.0 | 1 | 1 | untagged | - |
| config-feed-missing | 0.0 | 0.0 | 1 | 1 | untagged | - |
| controller-fed-pre-fee-amount | 0.0 | 0.0 | 1 | 1 | reincorporated | economic_attack.md |
| creation-refund-failure-stuck-funds | 0.0 | 0.0 | 1 | 1 | untagged | - |
| cross-function-reentrancy | 0.0 | 0.0 | 1 | 1 | untagged | - |
| deadline-blocktimestamp-noop | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| decimals-price-granularity | 0.0 | 0.0 | 1 | 1 | untagged | - |
| deprecated-market-baddebt | 0.0 | 0.0 | 1 | 1 | untagged | - |
| effectivebond-no-downward-correction | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md#16 |
| erc4626-ctoken-inflation | 0.0 | 0.0 | 1 | 1 | untagged | - |
| external-call-return-check | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md#13 |
| fee-cap-unit-mismatch | 0.0 | 0.0 | 1 | 1 | untagged | - |
| fee-change-between-submit-and-execute | 0.0 | 0.0 | 1 | 1 | untagged | - |
| fee-transparency | 0.0 | 0.0 | 1 | 1 | untagged | - |
| fot-bypass | 0.0 | 0.0 | 1 | 1 | untagged | - |
| global-param-change-affects-open-positions | 0.0 | 0.0 | 2 | 2 | reincorporated | logic.md |
| governance-weight-override | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| large-steps-dust | 0.0 | 0.0 | 1 | 1 | untagged | - |
| lender-fee-manipulation | 0.0 | 0.0 | 1 | 1 | untagged | - |
| leverage-accrual-revert | 0.0 | 0.0 | 1 | 1 | untagged | - |
| liq-reward-folded-into-premium | 0.0 | 0.0 | 1 | 1 | untagged | - |
| liquidation-mechanics | 0.0 | 0.0 | 1 | 1 | untagged | - |
| liquidation-sizing-ignores-bonus | 0.0 | 0.0 | 1 | 1 | reincorporated | economic_attack.md |
| listing-blocks-realloc | 0.0 | 0.0 | 1 | 1 | untagged | - |
| listing-type-validation | 0.0 | 0.0 | 1 | 1 | untagged | - |
| masterchef-rewarddebt-rounding | 0.0 | 0.0 | 1 | 1 | reincorporated | economic_attack.md |
| maxsell-auth | 0.0 | 0.0 | 1 | 1 | untagged | - |
| maxsell-bypass-via-bought | 0.0 | 0.0 | 1 | 1 | untagged | - |
| maxsell-delist-claim | 0.0 | 0.0 | 1 | 1 | untagged | - |
| memory-copy-state-write-lost | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| missing-liquidity-slippage | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| missing-sellable-check | 0.0 | 0.0 | 1 | 1 | untagged | - |
| missing-slippage | 0.0 | 0.0 | 1 | 1 | untagged | - |
| multiplier-default-zero-not-one | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| open-marginto-underflow | 0.0 | 0.0 | 1 | 1 | untagged | - |
| open-without-nft-ownership-check | 0.0 | 0.0 | 1 | 1 | untagged | - |
| oracle-balance-as-price | 0.0 | 0.0 | 1 | 1 | untagged | - |
| oracle-cumulative-price | 0.0 | 0.0 | 1 | 1 | untagged | - |
| oracle-deadlock | 0.0 | 0.0 | 1 | 1 | untagged | - |
| oracle-decimals | 0.0 | 0.0 | 1 | 1 | untagged | - |
| oracle-grief | 0.0 | 0.0 | 1 | 1 | untagged | - |
| oracle-inverted-price | 0.0 | 0.0 | 1 | 1 | untagged | - |
| oracle-stale-twap | 0.0 | 0.0 | 1 | 1 | untagged | - |
| oracle-twap-manipulation | 0.0 | 0.0 | 2 | 2 | untagged | - |
| oracle-unit-mismatch | 0.0 | 0.0 | 1 | 1 | untagged | - |
| oz-quorum-fraction-percent-misuse | 0.0 | 0.0 | 1 | 1 | reincorporated | access_control.md |
| pause-blocks-derisk-path | 0.0 | 0.0 | 1 | 1 | reincorporated | dos.md |
| pct-cap-below-abs-floor | 0.0 | 0.0 | 1 | 1 | reincorporated | dos.md |
| pol-changeranges-silent-fail | 0.0 | 0.0 | 1 | 1 | untagged | - |
| post-mint-config-mutation-harms-holders | 0.0 | 0.0 | 1 | 1 | untagged | - |
| post-op-invariant-comparison | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md#12 |
| price-guard-inversion | 0.0 | 0.0 | 1 | 1 | untagged | - |
| pricing-rounding | 0.0 | 0.0 | 1 | 1 | untagged | - |
| reclaim-grief-reopen | 0.0 | 0.0 | 1 | 1 | untagged | - |
| reentrancy-create | 0.0 | 0.0 | 1 | 1 | untagged | - |
| renewalcutoff-bypass-addpremium | 0.0 | 0.0 | 1 | 1 | untagged | - |
| round-boundary-decay-reset | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| self-bricking-setter | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md#9 |
| signature-not-bound-to-config-params | 0.0 | 0.0 | 1 | 1 | untagged | - |
| slope-underflow-dos | 0.0 | 0.0 | 1 | 1 | reincorporated | dos.md |
| stale-feegrowth-snapshot | 0.0 | 0.0 | 1 | 1 | untagged | - |
| stale-intermediate-state-gate | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| stale-param-at-action | 0.0 | 0.0 | 1 | 1 | untagged | - |
| stepduration-rounding | 0.0 | 0.0 | 1 | 1 | untagged | - |
| stranded-reward-swept-by-next-caller | 0.0 | 0.0 | 1 | 1 | reincorporated | economic_attack.md |
| strict-equality-balance-dos | 0.0 | 0.0 | 1 | 1 | reincorporated | dos.md |
| swap-no-slippage | 0.0 | 0.0 | 1 | 1 | untagged | - |
| token-callback-reentrancy | 0.0 | 0.0 | 1 | 1 | untagged | - |
| transfer-dos | 0.0 | 0.0 | 1 | 1 | untagged | - |
| transfer-includes-vested | 0.0 | 0.0 | 1 | 1 | untagged | - |
| tx-initiator-not-verified | 0.0 | 0.0 | 1 | 1 | reincorporated | access_control.md |
| unbounded-array-griefing | 0.0 | 0.0 | 1 | 1 | reincorporated | dos.md#10 |
| unconditional-native-refund-dos | 0.0 | 0.0 | 1 | 1 | reincorporated | dos.md |
| uni-feegrowth-underflow-revert-0.8 | 0.0 | 0.0 | 1 | 1 | untagged | - |
| unlist-locks-claimable | 0.0 | 0.0 | 1 | 1 | untagged | - |
| unlock-override-free-vote | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| unsigned-params-malleable | 0.0 | 0.0 | 1 | 1 | untagged | - |
| validation-forces-state-reopen | 0.0 | 0.0 | 1 | 1 | untagged | - |
| variable-overwrite | 0.0 | 0.0 | 1 | 1 | untagged | - |
| vote-power-stranded-on-gauge-removal | 0.0 | 0.0 | 1 | 1 | reincorporated | logic.md |
| wrong-pausable-base-transfers-not-blocked | 0.0 | 0.0 | 1 | 1 | untagged | - |
| zero-amount-external-call-reverts | 0.0 | 0.0 | 1 | 1 | reincorporated | token_integration.md |
| zero-transfer-revert-dos | 0.0 | 0.0 | 1 | 1 | untagged | - |
| checkpoint-timing-manipulation | 0.5 | 0.5 | 2 | 1 | reincorporated | economic_attack.md#9 |
| accrual-parity | 1.0 | 0.0 | 1 | 0 | reincorporated | behavioral_state_analysis.md#8 |
| basket-cross-asset-price-drift-arbitrage | 1.0 | 0.0 | 1 | 0 | untagged | - |
| cross-function-conservation | 1.0 | 0.0 | 1 | 0 | reincorporated | logic.md#14 |
| cross-service-reentrancy | 1.0 | 0.0 | 1 | 0 | reincorporated | reentrancy.md#6 |
| enumerablemap-zero-entries-not-pruned-gas-dos | 1.0 | 0.0 | 1 | 0 | untagged | - |
| fee-accounting-shared-position | 1.0 | 1.0 | 1 | 0 | reincorporated | economic_attack.md#8 |
| hand-rolled-index | 1.0 | 0.0 | 1 | 0 | reincorporated | logic.md#8 |
| handlereallocation-dos | 1.0 | 0.0 | 1 | 0 | untagged | - |
| inclusive-boundary-snapshot | 1.0 | 0.0 | 1 | 0 | reincorporated | logic.md#15 |
| internal-helper-exposed-public-no-access-control | 1.0 | 1.0 | 1 | 0 | untagged | - |
| lock-unlock-monotonicity | 1.0 | 0.5 | 2 | 0 | reincorporated | logic.md#10 |
| lp-burn-slippage | 1.0 | 0.0 | 1 | 0 | reincorporated | token_integration.md |
| lp-migration-precreated-pair-manipulation | 1.0 | 0.0 | 2 | 0 | untagged | - |
| missing-order-ownership-check | 1.0 | 0.333 | 3 | 0 | untagged | - |
| missing-sibling-check | 1.0 | 1.0 | 1 | 0 | caught | - |
| missing-token-validation | 1.0 | 0.0 | 1 | 0 | untagged | - |
| ordering-state-cleared-before-read | 1.0 | 1.0 | 1 | 0 | untagged | - |
| premium-portion-uint24-truncation | 1.0 | 0.0 | 2 | 0 | untagged | - |
| proportional-reward-split | 1.0 | 0.0 | 1 | 0 | untagged | - |
| pull-full-balance-not-amount | 1.0 | 0.0 | 1 | 0 | untagged | - |
| reentrancy-refund-callback-during-creation | 1.0 | 0.0 | 1 | 0 | untagged | - |
| refund-to-wrong-recipient | 1.0 | 0.0 | 1 | 0 | untagged | - |
| remainder-carryover | 1.0 | 0.0 | 2 | 0 | reincorporated | logic.md#11 |
| reward-computed-not-paid | 1.0 | 0.0 | 1 | 0 | untagged | - |
| reward-epoch-weight-misattribution | 1.0 | 0.0 | 2 | 0 | untagged | - |
| reward-transfer-revert-blocks-core-op | 1.0 | 0.0 | 1 | 0 | untagged | - |
| self-whitelist-bypass | 1.0 | 1.0 | 1 | 0 | reincorporated | access_control.md |
| signature-missing-deadline | 1.0 | 0.0 | 1 | 0 | reincorporated | access_control.md#7 |
| signature-missing-parameter | 1.0 | 0.0 | 1 | 0 | reincorporated | access_control.md#7 |
| signature-replay-claim | 1.0 | 0.0 | 1 | 0 | untagged | - |
| signed-validity-window | 1.0 | 1.0 | 1 | 0 | caught | - |
| single-sided-liquidity-grief | 1.0 | 1.0 | 1 | 0 | caught | - |
| stale-checkpoint-collateral-slash | 1.0 | 0.0 | 1 | 0 | untagged | - |
| step-underflow | 1.0 | 1.0 | 1 | 0 | untagged | - |
| swap-zero-minout-caller-routed | 1.0 | 1.0 | 1 | 0 | untagged | - |
| third-party-action-resets-victim-timelock | 1.0 | 1.0 | 1 | 0 | untagged | - |
| transferable-position-cap-bypass | 1.0 | 0.0 | 1 | 0 | reincorporated | economic_attack.md |
| underwater-liquidation-undercompensation | 1.0 | 0.0 | 1 | 0 | untagged | - |
| vesting-merge-stepsclaimed-ignored | 1.0 | 0.333 | 3 | 0 | untagged | - |
| wrong-mapping-key-ownership | 1.0 | 1.0 | 1 | 0 | untagged | - |
| wrong-variable-validated | 1.0 | 1.0 | 1 | 0 | untagged | - |

**Untested classes (in taxonomy, no awarded example yet — unmeasured blind spots):** move-address-param-not-signer-auth, evm-insecure-onchain-randomness, solana-insecure-onchain-randomness, move-insecure-onchain-randomness, move-onchain-data-not-private, solana-missing-signer-check, solana-missing-owner-check, solana-account-substitution-confusion, solana-missing-anchor-constraint, solana-reinit-missing-init-guard, solana-close-account-revival, solana-pda-seed-collision, solana-cpi-arbitrary-program, solana-remaining-accounts-trust, solana-arithmetic-unchecked, solana-pda-signer-seeds-missing-bump, solana-init-authority-mismatch-vs-use, solana-duplicate-mutable-account-serialization, init-once-guard-missing, default-sentinel-reward-routing-jit, critical-path-math-revert-dos, unreachable-guard-branch-ordering, bad-debt-socialization-par-exit, position-nft-callback-liquidation-dos, oracle-decimal-scaling-overflow, no-min-position-size-dust-baddebt, wrong-router-method-integration-revert, cross-chain-inbound-source-unauthenticated, approve-zero-reverts-blocks-teardown, lz-ordered-execution-option-missing, solana-account-count-config-mismatch-panic, solana-ed25519-introspection-data-unbound, solana-anchor-idl-instructions-enabled, reward-folded-into-liquidation-condition, stale-snapshot-before-mutation, ported-uni-0.8-underflow-revert, blacklist-token-push-refund-dos, act-on-unowned-external-asset, division-as-percentage-fee, stale-owner-snapshot-reward-attribution, counter-reset-ignores-preexisting-entries, cap-enforced-one-path-not-sibling, read-before-init-zero-default, missing-slippage-dynamic-price-op, no-exit-path-fund-lockup, signature-missing-chainid-replay, signature-scope-gap-unsigned-params, map-entry-zeroed-not-removed-gas-dos, wrong-pausable-base-no-transfer-block, reentrancy-refund-before-state-finalize, post-commitment-config-mutation, param-sanity-cap-wrong-unit, move-clmm-liquidity-overflow, move-rounding-direction, move-signed-int-tick-math, move-coin-balance-conservation, move-hot-potato-bypass, move-capability-safety, move-object-ownership, move-constant-product-invariant-recheck, move-public-helper-visibility, fee-charged-outside-allowance, forwarder-request-missing-deadline, unchecked-erc20-approve-return, solana-lamport-invariant-includes-rent, fee-tier-boundary-discontinuity
