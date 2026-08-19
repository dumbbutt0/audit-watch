# AC-001 — RESCUER can drain the GM marketToken/poolToken (the deployed vault value) via `rescueFunds` — only the USDC asset is protected

| | |
|---|---|
| **Severity** | **Medium** (privileged drain of the entire deployed reserve via a mis-scoped guard; deflates share price for every honest locker) |
| **Category (HackenProof VRT)** | Improper Access Control |
| **Target** | Cartha Vaults (`cartha-vaults-main`, commit `4c51f2a8915f438976b57134d646b55199a11318`) |
| **Contracts** | `src/CarthaVault.sol` (`rescueFunds`, line 617) |
| **Attacker** | A holder of `Roles.RESCUER` (the emergency-recovery role) that is compromised or malicious — privileged, not permissionless |
| **PoC** | `poc/PoC_RescuerDrainsGM_AC001.t.sol` (passing — `poc/run_output.txt`) |

## Not a duplicate of the TVL-valuation findings

This is a **rescue-function access-control defect**, in a different subsystem from CARTHA-SEAM-001 (GM decimal scale), DT-001 (async window), and DOS-001 (cross-child revert). It is not about *how GM is valued* or *when* — it is that the value-bearing GM token can be **transferred out** through a guard that only protects the USDC asset. It survives all three of those fixes.

## Summary

`CarthaVault.rescueFunds(token, recipient, amount)` is gated by `Roles.RESCUER` and is meant to recover **stray, non-vault tokens** — it explicitly blocks `token == $.asset` (the 6-decimal USDC accounting asset) to avoid touching vault value. But a child vault's real value, once a keeper deploys idle USDC into a 0xMarkets pool, lives in `$.marketToken` / `$.poolToken` (the GM market token), **not** in the USDC asset. Those tokens are **not** on the block-list, so a RESCUER can call `rescueFunds(marketToken, attacker, fullBalance)` and ship the entire GM-deployed position out of the vault. This both (a) removes the real value backing user shares and (b) silently lowers `_gmValueInUsdc` → `_totalValueLocked`, deflating `sharePrice` and every subsequent `_convertToAssets` payout (release / forceExit / processQueuedWithdrawals) for honest lockers.

## Vulnerability detail

```solidity
// src/CarthaVault.sol:617-626
function rescueFunds(address token, address recipient, uint256 amount) external onlyRole(Roles.RESCUER) {
    CarthaVaultStorage storage $ = _getCarthaVaultStorage();
    if (token == $.asset) revert CannotRescueVaultAsset();   // <-- ONLY the USDC asset is protected
    if (recipient == address(0)) revert InvalidRecipient();
    if (amount == 0) revert InvalidAmount();

    IERC20(token).safeTransfer(recipient, amount);           // <-- any OTHER token (incl. GM) ships out
    emit FundsRescued(token, recipient, amount);
}
```

The vault's value is computed as USDC balance + the GM position:

```solidity
// src/CarthaVault.sol:944  (_totalValueLocked -> _gmValueInUsdc)
return PoolDeployLib.gmValueInUsdc(address($.poolToken), $.reader, $.dataStore, $.marketToken, $.oracle);
```

So `marketToken`/`poolToken` are exactly the value-bearing tokens — and exactly the ones the block-list omits. The guard's intent (don't let `rescueFunds` touch vault value) is correct; its **scope is incomplete** (it lists the asset but not the GM tokens that hold the deployed value).

## Impact

A compromised or malicious RESCUER drains the vault's entire GM `marketToken`/`poolToken` (the deployed reserve) to an arbitrary address. This:
- directly removes the real value backing user shares, and
- collapses `_gmValueInUsdc` → `_totalValueLocked`, so `sharePrice` and every honest locker's `release` / force-exit / queued-withdrawal payout are reduced pro-rata — their redemptions now pay out a fraction of principal.

The error also propagates to the parent: `CarthaParentVault.totalAssets()` reads `child.totalValueLocked()`, so draining one child deflates the whole parent's TVL and every parent LP's claim.

> Honesty caveat: `RESCUER` is a privileged role (emergency multisig), so this is not permissionless — impact is bounded by trust in that key, hence **Medium**. It is reported as a concrete code defect (an incomplete block-list that defeats the developer's own value-protection intent), not a generic "trusted role can misbehave": the negative control in the PoC shows the guard *does* protect the USDC asset, and only the GM tokens slip through.

## Step-by-step (from the PoC)

1. Incumbent LP locks **$1,000,000** → $500k to each of two children. Keeper deploys $250k of child B into the 0xM pool; the 0xM keeper executes → **child B holds $250k of GM**.
2. **Baseline:** child B `totalValueLocked() == $500,000` (250k idle + 250k GM), parent `totalAssets() == $1,000,000`, incumbent's redeemable claim `== $1,000,000`.
3. The RESCUER role is granted to the attacker (models a compromised/malicious emergency key).
4. **Negative control:** `rescueFunds(USDC, attacker, 1)` **reverts** `CannotRescueVaultAsset` — the guard protects the asset.
5. **The bug:** `rescueFunds(marketToken, attacker, gmBalance)` **succeeds** — the entire GM position transfers to the attacker.
6. **After:** attacker holds the full $250k of GM; child B `totalValueLocked()` collapses to **$250,000** (idle USDC only), parent `totalAssets()` drops to **$750,000**, and the incumbent's redeemable claim falls to **$750,000** — a **~$250,000 permanent loss** of backing for the honest locker.

```
child B TVL before/after     : 500000000000 -> 250000000000
parent TVL before/after      : 1000000000000 -> 750000000000
incumbent claim before/after : 1000000000000 -> 750000000000
attacker GM gained           : 250000000000   (the deployed reserve)
incumbent principal lost      : 250000000000
```

## Recommended fix

Extend the `rescueFunds` block-list to the value-bearing tokens, not just the asset:

```solidity
if (token == $.asset || token == $.marketToken || token == $.poolToken) revert CannotRescueVaultAsset();
```

(Or invert the design: only allow rescuing tokens that are *not* part of vault accounting — an allow-list of explicitly-stray tokens — so any future value-bearing token is protected by default.)

## Re-verification note

Re-verified end-to-end with the project's own Foundry harness (parent + 2 children via `CarthaVaultFactory`, real `depositAndLockSpread` / `deployToPool` flows, GM valued correctly via the project mocks). The PoC asserts the full chain: the negative control proves the USDC guard fires, then `rescueFunds(marketToken)` drains the GM, `totalValueLocked()` / `totalAssets()` deflate by the stolen amount, and the incumbent's pro-rata claim drops ~$250k. Test passes (`poc/run_output.txt`). Self-contained — no external dependencies (`forge test --match-path "test/poc/PoC_RescuerDrainsGM_AC001.t.sol" -vv`).
