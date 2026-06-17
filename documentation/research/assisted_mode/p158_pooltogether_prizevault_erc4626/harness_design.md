# P158 — Harness Design (intended) + why runtime was NOT_RUN_TOO_HEAVY

## What a faithful harness would have been
A real-contract negative control proving the source refutation:
1. Deploy real `PrizeVault` + `MockAsset` (ERC20) + `MockYieldVault` (ERC4626, manipulable rate to simulate
   loss) + `MockTwabController` (balanceOf/totalSupply/mint/burn/transfer, uint96) + `MockPrizePool`
   (returns the twabController; stub prizeToken/contributePrizeTokens).
2. **Control:** healthy state → `deposit` mints 1:1, `withdraw`/`redeem` return ~1:1.
3. **Refutation A:** induce a yield-vault loss, then `deposit` → expect **`LossyDeposit` revert**.
4. **Refutation B:** in a lossy state, `withdraw`/`redeem` → expect a **debt-aware haircut** (no 1:1
   over-withdrawal).
Mock surface is small (`yieldVault.{balanceOf,convertToAssets,maxDeposit,maxRedeem,maxWithdraw,mint,
previewDeposit,previewWithdraw,redeem,withdraw}`; `twabController.{balanceOf,totalSupply,mint,burn,transfer}`;
`prizePool.{twabController}`).

## Why it was NOT built (deploy_too_heavy)
The blocker is **compilation of the real `PrizeVault`**, not the mocks:
- `PrizeVault` inherits `TwabERC20` (imports the **concrete** `pt-v5-twab-controller/TwabController`) and
  `Claimable` (imports the **concrete** `pt-v5-prize-pool/PrizePool` + `pt-v5-claimable-interface` +
  `HookManager`), plus `owner-manager-contracts/Ownable` and `pt-v5-liquidator-interfaces`.
- **None of these packages are vendored** in `audits/pooltogether-2024-03-holdout/` and there is no
  `remappings.txt`/`foundry.toml`. `PrizePool` is a large dependency tree (draw/tier/observation libs).
- To compile the real contract one must fetch the full pt-v5 dependency graph → **not deploy-light**;
  building it for one campaign phase is disproportionate, and — critically — **the mechanism is already
  refuted at source** by the `LossyDeposit` guard + debt-aware previews, so a runtime PoC would only
  re-confirm a plainly-read revert.

## Decision
`runtime_status = not_run` (`deploy_too_heavy`); the candidate is recorded as a **source-level
static_false_positive** (guarded). No PoC directory was created (nothing was deployed/run). The
`_sealed_answer_key/` was not opened.
