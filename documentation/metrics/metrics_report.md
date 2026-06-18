# Pipeline Metrics (cross-audit)

_Generated 2026-06-18T01:14:51.028771+00:00 · 11 audits · 0 ground-truth records._

> Rates are over findings that HAVE a recorded human outcome. Low ground_truth_records ⇒ metrics are directional, not yet robust.

| Metric | Value |
|---|---|
| False-positive rate | unmeasured (no ground truth) |
| Recall on valid findings | unmeasured (no ground truth) |
| Valid-finding rate | unmeasured (no ground truth) |
| Duplicate rate | unmeasured (no ground truth) |
| Severity-downgrade rate | unmeasured (no ground truth) |
| PoC success rate | unmeasured (no ground truth) |

## Per-agent reliability (valid / valid+invalid, ground-truth'd only)

| Agent | Reliability | n |
|---|---|---|

## Per-bug-class reliability

| Bug class | Reliability | n |
|---|---|---|

## Detection-lens inventory (mechanism classes — read-only capability)

_98 reincorporated · 102 eval-anchored · 112 total. Lens/mechanism-class capability inventory (read-only from config/mechanism_classes.json). 'reincorporated' = authored from a real or measured eval finding (proven recall lever); 'eval_anchored' = has >=1 awarded_examples. Distinct from real-world FP/recall, which need ground-truth outcomes._

| Language | Total | Reincorporated | Seeded | Eval-anchored |
|---|---|---|---|---|
| move | 12 | 5 | 7 | 5 |
| rust | 18 | 15 | 3 | 15 |
| solidity | 82 | 78 | 0 | 82 |

### Reincorporated lenses (proven recall levers)

| Lens (mechanism class) | Lang | Prompt section | Awarded examples |
|---|---|---|---|
| move-address-param-not-signer-auth | move | move_object_capability.md#8 | secret-vault-aptos-2025-07-blind:H-02 |
| move-constant-product-invariant-recheck | move | move_clmm_math.md#7 | sui-amm-swap-2022-11-eval:M-1 |
| move-insecure-onchain-randomness | move | move_object_capability.md#10 | pizza-drop-aptos-2025-08-blind:M-01 |
| move-onchain-data-not-private | move | move_object_capability.md#9 | secret-vault-aptos-2025-07-blind:H-01 |
| move-public-helper-visibility | move | move_object_capability.md#7 | sui-amm-swap-2022-11-eval:M-4 |
| lz-ordered-execution-option-missing | rust | solana_cpi.md | orderly-solana-2024-10-eval:M-1 |
| solana-account-count-config-mismatch-panic | rust | solana_cpi.md | lz-solana-endpoint-zellic-2024:M-3.3 |
| solana-account-substitution-confusion | rust | solana_account_model.md | lz-solana-endpoint-zellic-2024:H-3.2 |
| solana-anchor-idl-instructions-enabled | rust | solana_account_model.md | drift-zellic-2022:anchor-idl-enabled |
| solana-arithmetic-unchecked | rust | solana_account_model.md | drift-zellic-2022:unchecked-division, drift-zellic-2022:signed-division-rounding |
| solana-close-account-revival | rust | solana_account_model.md | lz-solana-endpoint-zellic-2024:H-3.1 |
| solana-duplicate-mutable-account-serialization | rust | solana_account_model.md | woofi-solana-2024-08-eval:M-3 |
| solana-ed25519-introspection-data-unbound | rust | solana_cpi.md | pyth-lazer-solana-2024-eval:3.1 |
| solana-init-authority-mismatch-vs-use | rust | solana_account_model.md | woofi-solana-2024-08-eval:M-1 |
| solana-lamport-invariant-includes-rent | rust | SOL/lamport-balance invariant must EXCLUDE the rent-exempt minimum | pump-science-2025-01-blind:M-02 |
| solana-missing-anchor-constraint | rust | solana_account_model.md | woofi-solana-2024-08-eval:H-2, orderly-solana-2024-10-eval:H-1, orderly-solana-2024-10-eval:H-2 |
| solana-missing-signer-check | rust | solana_account_model.md | woofi-solana-2024-08-eval:M-2 |
| solana-pda-signer-seeds-missing-bump | rust | solana_cpi.md | woofi-solana-2024-08-eval:H-1 |
| solana-reinit-missing-init-guard | rust | solana_account_model.md | pyth-lazer-solana-2024-eval:3.2 |
| solana-remaining-accounts-trust | rust | solana_cpi.md | lz-solana-endpoint-zellic-2024:M-3.3 |
| aa-wallet-cross-chain-address | solidity | cross_chain.md | nudgexyz-2025-03-blind:M-03 |
| accrual-parity | solidity | behavioral_state_analysis.md#8 | munchables-2024-05-holdout:M-04 |
| act-on-unowned-external-asset | solidity | access_control.md | particle-2023-12-blind:M-12 |
| approve-zero-reverts-blocks-teardown | solidity | token_integration.md | silo-finance-2025-03-strict-eval:M-03 |
| bad-debt-socialization-par-exit | solidity | economic_attack.md | panoptic-2025-12-strict-eval:M-19 |
| blacklist-token-push-refund-dos | solidity | dos.md | particle-2023-12-blind:H-01 |
| bps-sqrt-precision-loss | solidity | logic.md | numa-2024-12-eval:M-10 |
| cached-config-not-refetched | solidity | logic.md#40 | phi-2024-08-blind:M-06 |
| cap-enforced-one-path-not-sibling | solidity | logic.md#37 | traitforge-2024-07-blind:H-05 |
| checkpoint-timing-manipulation | solidity | economic_attack.md#9 | olas-2026-01-blind:M-10 |
| controller-fed-pre-fee-amount | solidity | economic_attack.md | numa-2024-12-eval:M-13 |
| counter-reset-ignores-preexisting-entries | solidity | logic.md#36 | traitforge-2024-07-blind:H-04 |
| critical-path-math-revert-dos | solidity | dos.md | panoptic-2025-12-strict-eval:M-05, panoptic-2025-12-strict-eval:M-08, panoptic-2025-12-strict-eval:M-01 |
| cross-chain-inbound-source-unauthenticated | solidity | cross_chain.md | centrifuge-2023-09-holdout:M-01, decent-2024-01-holdout:M-03 |
| cross-function-conservation | solidity | logic.md#14 | monetrix-2026-04-blind:M-01 |
| cross-service-reentrancy | solidity | reentrancy.md#6 | olas-2026-01-blind:H-05 |
| deadline-blocktimestamp-noop | solidity | logic.md | particle-2023-12-blind:M-02 |
| default-sentinel-reward-routing-jit | solidity | economic_attack.md | panoptic-2025-12-strict-eval:M-15 |
| division-as-percentage-fee | solidity | arithmetic.md | traitforge-2024-07-blind:H-03 |
| effectivebond-no-downward-correction | solidity | logic.md#16 | olas-2026-01-blind:M-09 |
| external-call-return-check | solidity | logic.md#13 | badger-2024-06-holdout:M-02 |
| fee-accounting-shared-position | solidity | economic_attack.md#8 | vultisig-2024-06-holdout:H-01 |
| fee-charged-outside-allowance | solidity | Fee charged OUTSIDE the approved allowance (fee-on-transfer in transferFrom) | next-generation-2025-01-blind:M-01 |
| fee-tier-boundary-discontinuity | solidity | Piecewise fee/rate curve DISCONTINUITY at a tier boundary | pump-science-2025-01-blind:M-03 |
| forwarder-request-missing-deadline | solidity | Meta-tx FORWARDER request has no deadline/expiry | next-generation-2025-01-blind:M-03 |
| global-param-change-affects-open-positions | solidity | logic.md | particle-2023-12-blind:M-05 |
| governance-weight-override | solidity | logic.md | neobase-2024-03-blind:M-03 |
| hand-rolled-index | solidity | logic.md#8 | kleidi-2024-10-holdout:M-02 |
| inclusive-boundary-snapshot | solidity | logic.md#15 | intuition-2026-03-blind:M-02 |
| init-once-guard-missing | solidity | access_control.md | panoptic-2025-12-strict-eval:H-01 |
| liquidation-sizing-ignores-bonus | solidity | economic_attack.md | cap-2025-07-eval:M-10 |
| lock-unlock-monotonicity | solidity | logic.md#10 | munchables-2024-05-holdout:H-01, munchables-2024-05-holdout:H-02 |
| lp-burn-slippage | solidity | token_integration.md | vultisig-2024-06-holdout:M-02 |
| map-entry-zeroed-not-removed-gas-dos | solidity | dos.md#19 | phi-2024-08-blind:H-03 |
| masterchef-rewarddebt-rounding | solidity | economic_attack.md | neobase-2024-03-blind:M-05 |
| memory-copy-state-write-lost | solidity | logic.md | init-capital-2024-01-blind:M-02 |
| missing-liquidity-slippage | solidity | logic.md | particle-2023-12-blind:M-15 |
| missing-slippage-dynamic-price-op | solidity | economic_attack.md#11 | traitforge-2024-07-blind:M-04, traitforge-2024-07-blind:M-16, phi-2024-08-blind:M-03 |
| multiplier-default-zero-not-one | solidity | logic.md | cap-2025-07-eval:M-6 |
| no-exit-path-fund-lockup | solidity | dos.md#18 | traitforge-2024-07-blind:M-02 |
| no-min-position-size-dust-baddebt | solidity | economic_attack.md | revert-lend-2024-03-strict-eval:M-03 |
| oracle-decimal-scaling-overflow | solidity | oracle.md | revert-lend-2024-03-strict-eval:M-07 |
| oz-quorum-fraction-percent-misuse | solidity | access_control.md | iq-ai-2025-01-blind:H-01 |
| param-sanity-cap-wrong-unit | solidity | arithmetic.md | phi-2024-08-blind:M-02 |
| pause-blocks-derisk-path | solidity | dos.md | cap-2025-07-eval:M-4 |
| pct-cap-below-abs-floor | solidity | dos.md | numa-2024-12-eval:M-14 |
| ported-uni-0.8-underflow-revert | solidity | arithmetic.md | particle-2023-12-blind:H-04 |
| position-nft-callback-liquidation-dos | solidity | reentrancy.md#6 | revert-lend-2024-03-strict-eval:H-06 |
| post-commitment-config-mutation | solidity | logic.md#39 | phi-2024-08-blind:H-07, phi-2024-08-blind:H-04 |
| post-op-invariant-comparison | solidity | logic.md#12 | badger-2024-06-holdout:M-01 |
| read-before-init-zero-default | solidity | logic.md#38 | traitforge-2024-07-blind:M-01 |
| reentrancy-refund-before-state-finalize | solidity | reentrancy.md | phi-2024-08-blind:H-06 |
| remainder-carryover | solidity | logic.md#11 | munchables-2024-05-holdout:M-02, munchables-2024-05-holdout:M-03 |
| reward-folded-into-liquidation-condition | solidity | logic.md | particle-2023-12-blind:M-06 |
| round-boundary-decay-reset | solidity | logic.md | numa-2024-12-eval:M-1 |
| self-bricking-setter | solidity | logic.md#9 | kleidi-2024-10-holdout:M-03 |
| self-whitelist-bypass | solidity | access_control.md | vultisig-2024-06-holdout:H-02 |
| signature-missing-chainid-replay | solidity | access_control.md | phi-2024-08-blind:H-01 |
| signature-missing-deadline | solidity | access_control.md#7 | olas-2026-01-blind:H-07 |
| signature-missing-parameter | solidity | access_control.md#7 | olas-2026-01-blind:H-09 |
| signature-scope-gap-unsigned-params | solidity | access_control.md | phi-2024-08-blind:H-02, phi-2024-08-blind:M-05 |
| slope-underflow-dos | solidity | dos.md | neobase-2024-03-blind:M-01 |
| stale-intermediate-state-gate | solidity | logic.md | cap-2025-07-eval:M-1 |
| stale-owner-snapshot-reward-attribution | solidity | logic.md#35 | traitforge-2024-07-blind:H-02 |
| stale-snapshot-before-mutation | solidity | logic.md | particle-2023-12-blind:H-02 |
| stranded-reward-swept-by-next-caller | solidity | economic_attack.md | cap-2025-07-eval:M-8 |
| strict-equality-balance-dos | solidity | dos.md | init-capital-2024-01-blind:M-03 |
| transferable-position-cap-bypass | solidity | economic_attack.md | vultisig-2024-06-holdout:M-03 |
| tx-initiator-not-verified | solidity | access_control.md | nudgexyz-2025-03-blind:M-04 |
| unbounded-array-griefing | solidity | dos.md#10 | kleidi-2024-10-holdout:M-01 |
| unchecked-erc20-approve-return | solidity | Unchecked ERC20 approve()/transfer() return — raw call instead of SafeERC20 | garden-2025-11-blind:M-01 |
| unconditional-native-refund-dos | solidity | dos.md | init-capital-2024-01-blind:M-01 |
| unlock-override-free-vote | solidity | logic.md | neobase-2024-03-blind:M-07 |
| unreachable-guard-branch-ordering | solidity | logic.md | panoptic-2025-12-strict-eval:M-17, panoptic-2025-12-strict-eval:M-18 |
| vote-power-stranded-on-gauge-removal | solidity | logic.md | neobase-2024-03-blind:H-01 |
| wrong-pausable-base-no-transfer-block | solidity | dos.md#20 | phi-2024-08-blind:M-01 |
| wrong-router-method-integration-revert | solidity | token_integration.md | zetachain-2023-10-holdout:H-10 |
| zero-amount-external-call-reverts | solidity | token_integration.md | cap-2025-07-eval:M-3 |
