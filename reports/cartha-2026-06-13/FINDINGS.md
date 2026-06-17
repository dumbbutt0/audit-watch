# Cartha Vaults — audit findings

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Source: user-provided `cartha-vaults-main.zip` → `/tmp/cartha-hunt/cartha-vaults-main/` (commit `4c51f2a…`).
Target: Cartha — Bittensor SN35 liquidity vaults. Parent vaults spread USDC across child vaults by weight; children
deploy idle USDC into **0xMarkets** (GMX-style) GM-token perp pools. ERC4626-ish 18-dec shares with **custom**
`_convertToShares/_convertToAssets`; EIP-712 (EJECTOR) miner locks; async keeper deploy/recall + queues; Diamond
role access control; UUPS + factory/BeaconProxy. Foundry, `solc ^0.8.20`.

Toolchain: empty `lib/` populated from cache (forge-std + OZ 5.4 [pinned 5.5] + OZ-upgradeable + solady). `forge build`
clean. Baseline `forge test --no-match-path 'test/fork/**'` = **283 passed / 0 failed** (repo ships full 0xM mocks +
signature/merkle utils → PoCs need no fork).

---

## C-1 (HIGH) — Stale/zero-TVL share mispricing lets a depositor steal existing holders' PnL
> **Reachability confirmed** (2026-06-13): auditing 0xMarkets shows `MarketUtils.getMarketTokenPrice` returns `0`
> when `poolValue == 0` and negative when `poolValue < 0` (signed `int256`) — a real market state — so the `gmPrice ≤ 0`
> precondition holds and this is rated **High**. See `cartha-C1-reachability.md`.

**Contracts:** `src/CarthaVault.sol :: _convertToShares` + `_totalValueLocked`; `src/libraries/PoolDeployLib.sol ::
gmValueInUsdc`. (Same shape exists in `CarthaParentVault._convertToShares` over `totalAssets()`.)
**Status:** CONFIRMED with a passing Foundry PoC (`PoC_StaleTvlMint.t.sol`).

### Root cause
Share minting prices deposits off live TVL, but the conversion silently falls back to the **first-deposit rate**
(1e12 decimal offset) whenever TVL reads zero — even when `totalSupply > 0`:

```solidity
// CarthaVault._convertToShares
uint256 totalShares = totalSupply();
uint256 totalAssets_ = _totalValueLocked();          // = idle USDC + GM value
if (totalShares == 0 || totalAssets_ == 0) {         // <-- treats TVL==0 as a brand-new vault
    return assets * 10 ** (decimals() - IERC20Metadata($.asset).decimals());   // 1e12 offset
}
return (assets * totalShares) / totalAssets_;        // live price (the correct branch)
```

`_totalValueLocked = idle + PoolDeployLib.gmValueInUsdc(...)`, and `gmValueInUsdc` **returns 0 when the 0xM market
token price is `<= 0`** (`if (gmPrice <= 0) return 0;`). So if a child's idle USDC is largely deployed (idle ≈ 0)
and the 0xM oracle reports `gmPrice <= 0`, `_totalValueLocked()` reads **0 while real, profitable GM value still
exists**, and any `depositAndLock` (permissionless) mints at the stale 1e12 first-deposit rate instead of the live,
higher price. The over-minted shares dilute existing holders' PnL.

The project itself treats `gmPrice <= 0` as a real scenario — see `test/vault/CarthaVaultPool.t.sol ::
test_TVL_HandlesNegativeGmPrice`. (GMX-style market token price can go negative when cumulative trader PnL exceeds
the pool's `MAX_PNL_FACTOR_FOR_DEPOSITS` — exactly the factor `_getGmPrice` requests.) The async deploy/recall window
(USDC in-flight to 0xM, GM not yet minted) is a milder variant that also undercounts TVL.

### Impact
Direct theft of existing depositors' accrued PnL by a permissionless depositor during a zero-TVL read. PoC: a vault
with a 100k-USDC position grown to 150k (GM value, idle drained); oracle reads `gmPrice = 0` → TVL reads 0; attacker
`depositAndLock(100k)` mints at the first-deposit rate; after the price recovers the attacker can claim **125k for a
100k deposit** and the victim drops **150k → 125k (25k stolen)**. Severity **High**: the `gmPrice ≤ 0` precondition is
confirmed reachable (0xM `getMarketTokenPrice` is signed and returns ≤ 0 when `poolValue ≤ 0`); exploitation needs the
child's idle ≈ fully deployed at the read.

### PoC (`PoC_StaleTvlMint.t.sol`, passing)
`forge test --match-contract PoC_StaleTvlMint -vv`. Logs: attacker deposited 100k → claim 125k; victim 150k → 125k.

### Fix
Do **not** fall back to the first-deposit rate when `totalSupply > 0`: if `totalSupply > 0 && totalAssets_ == 0`,
revert (or pause minting) rather than mint at 1e12. Treat a `<= 0` / stale GM price as a hard error for
mint/redeem pricing (revert), not as `TVL += 0`. Consider a deposit `minSharesOut` and an oracle freshness check.

---

## L-1 (LOW) — Parent `withdraw` / `releaseFromParent` burn full shares but can underpay on rounding

`CarthaParentVault.withdraw` burns `_convertToSharesRoundUp(assets)` and `releaseFromParent`/`processQueuedParent
Withdrawals` burn the full `lockedShares`, but the payout is `min(value, balance)` after `_withdrawFromChildren`,
which does a **single proportional pass** (`withdrawAmount = amount * parentPortion / totalIdle`, floored per child)
and never loops to cover the rounding remainder. The `_availableFromChildren() + 10 < needed` guard tolerates ~10
wei. Net: the caller can burn shares worth `assets` but receive slightly less (dust). Bounded; Low.
**Fix:** pay exactly `shareValue`/`assets` (revert if not fully covered) or burn shares proportional to the actual
payout.

## L-2 (LOW) — Child shares are transferable post-lock but only redeemable via a Position

`CarthaVault` exposes no permissionless `redeem`-by-shares; redemption is position-bound (`release`/`forceExit`/
`processQueuedWithdrawals`, capped at the owner's position). ERC20 shares are transferable once the lock expires
(`_update`). Shares moved to an address without a Position are **orphaned** (non-redeemable) yet still count in
`totalSupply` (diluting `_convertToAssets` for everyone). Footgun / potential user fund loss if shares are traded.
**Fix:** make shares non-transferable, or add a position-independent redeem, or document the constraint.

## Info
- **GM-held TVL valuation** uses `getMarketTokenPrice(..., MAX_PNL_FACTOR_FOR_DEPOSITS, false)` — the deposit-side,
  minimized valuation for tokens the vault would *redeem*; consider the withdrawal pnl factor / correct min-max.
- **Penalty inconsistency:** `CarthaForceExit` hardcodes 5% underperformer penalty; `CarthaVault.forceExitUnderperformer`
  uses the configurable `performancePenalty`.
- **Async deploy/recall gap:** between `deployToPool` and 0xM keeper execution, the in-flight USDC is neither idle nor
  GM, so TVL is undercounted for the window (milder C-1 variant; the dramatic first-deposit-rate case needs idle≈0
  with GM still held, i.e. the `gmPrice<=0` path).

## Surfaces reviewed & sound
- **EIP-712 locks** (`_verifyLockSignature`/`_verifyParentLockSignature`): domain-bound (`_hashTypedDataV4`),
  per-owner nonce in the struct, EJECTOR role enforced, OZ `ECDSA.recover` (rejects malleable/zero). No replay.
- **Cross-vault conservation:** `withdrawToParent` burns the parent's child-shares (ceil, vault-favoring) → child TVL
  isn't double-counted in parent TVL; direct-child vs via-parent deposits share child TVL pro-rata correctly;
  `rebalance`/`shiftLiquidity` conserve value (keeper-gated).
- **Classic 4626 inflation:** the 1e12 share offset makes the donation rounding-to-zero attack require an absurd
  donation; atomic oracle-sandwich on deposit is blocked by the mandatory lock + cooldown.
- **Upgrade/init/access:** constructors `_disableInitializers()`; `initialize` is `initializer`-gated; BeaconProxy
  init is atomic (no front-run); `_authorizeUpgrade` ADMIN-only; `diamondCut` owner-gated; `grant/revokeRole`
  ADMIN-gated; `rescueFunds` cannot touch the vault asset.

## Bottom line
**One confirmed High (C-1, stale/zero-TVL share mispricing → PnL theft) with a passing PoC** (reachability confirmed
via the 0xMarkets audit), plus two Lows
and Info notes. The auth/upgrade/conservation/signature surfaces are sound. **Nothing submitted** — the user reviews
and submits. Severity of C-1 hinges on the 0xM oracle's `<= 0` reachability (the repo treats it as expected) — worth
confirming against 0xMarkets' live market-token-price behavior before filing.
