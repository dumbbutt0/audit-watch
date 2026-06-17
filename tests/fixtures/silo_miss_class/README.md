# Silo Finance miss-class fixtures (reconstructed)

Minimal reconstructed Solidity for the Silo Finance strict-eval misses that this forward-looking patch
targets, plus safe equivalents for FP control. Shapes are derived from the eval `failure_analysis.md`
(`documentation/evals/silo-finance-2025-03/strict_eval_report.md` §12) — **no answer-key text copied**.
Illustrative only; the enforced regression is the disposition-level routing test
`tests/deep_solidity/test_silo_miss_class_replay.py` (which drives `coverage_sweep_write`, `bridge_terms`,
and `waiver_utils` directly) plus the read-only frozen-snapshot replay.

The Silo HIT (M-05 feeShares minting order) was already converted by the shipped erc4626 `feeshares_order`
field — the lesson was **enforced checklist surfaces convert; unenforced ideas don't**. These fixtures cover
the *newly enforced* surfaces.

| Miss | File | Shape | New control that catches it |
|---|---|---|---|
| M-02 | `m02_transfer_reward_unsynced_totalsupply.sol` | share transfer accrues reward against a `totalSupply` not synced with pending fee shares; balance snapshot after mutation | **reward_accounting checklist** (`totalsupply_sync_before_accrual`, `transfer_side_effects`, `rewards_on_share_transfer`, `balance_snapshot_timing`) |
| M-04 | `m04_missing_slippage_deadline.sol` | deposit/redeem with no `minOut`/`minShares` and no deadline → sandwich/share-price exposure | **slippage_deadline checklist** (`min_out_protection`, `deadline_bound`, `user_bounds_received`) |
| M-06 | `m06_vault_market_deflation_rounding.sol` | user-share layer OZ-safe, but vault→market supply rounds the strategy receipt down and socializes the loss | **vault_market_inflation_deflation checklist** (`vault_market_deposit_traced`, `market_rounding`, `strategy_receipt_amount`, `downstream_rounding_loss`, `loss_attribution`) |
| bridge FP | `bridge_false_trigger_vault_verbs.sol` | plain vault deposit/withdraw/mint with a `recipient` param, **no** cross-chain context | **bridge-lens round 2** — generic vault verbs demoted; thread is NOT bridge-escalated (`_safe.sol` adds an L2 endpoint + cross-chain message → SHOULD escalate) |
| waiver | `reallocate_flowcap_high_risk_waiver.sol` | `reallocateTo` / `setFlowCaps` move funds + set caps | **waiver discipline** — `risk_class == vault_accounting`, high-risk → cannot be cluster-waived (`_safe.sol` is an unrelated metadata view = low-risk) |

Each `*.sol` has a `*_safe.sol` sibling that is either the corrected version (M-02/M-04/M-06) or the
positive-control that *should* still trigger the control (bridge / waiver), proving the controls are precise
rather than blanket.
