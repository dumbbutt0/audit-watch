# DT-001 — Share dilution via the asynchronous 0xMarkets deploy/recall window (in-flight value uncounted in TVL)

| | |
|---|---|
| **Severity** | **High** (permissionless value extraction from existing depositors) |
| **Category (HackenProof VRT)** | Transaction-Ordering Dependence (TOD) / Front Running |
| **Target** | Cartha Vaults (`cartha-vaults-main`, commit `4c51f2a8915f438976b57134d646b55199a11318`) |
| **Contracts** | `src/CarthaVault.sol`, `src/libraries/PoolDeployLib.sol` (propagates to `src/CarthaParentVault.sol`) |
| **Attacker** | Permissionless — any account with ≥ `minimumLockAmount` (100k USDC), observing the public keeper tx |
| **PoC** | `poc/PoC_AsyncWindowDilution.t.sol` (passing — `poc/run_output.txt`) |

## Not a duplicate of CARTHA-SEAM-001 / ZEROMARK-553 (the GM decimal-scale bug)

This is **independent** of the GM decimal mismatch (CARTHA-SEAM-001, HackenProof **ZEROMARK-553**). The over-mint occurs in the window when the vault holds *neither* USDC (sent to the 0xM depositVault, `PoolDeployLib.deploy`) *nor* GM (minted later by the keeper, a separate tx). `_totalValueLocked()` (`CarthaVault.sol:940`) reads current balances only, so it understates TVL by the in-flight amount **regardless of how the GM leg is scaled** — fixing ZEROMARK-553's decimal normalization does not restore the missing value. The PoC isolates it by valuing GM **correctly** (`setMarketTokenPrice(1e30)` + matching 1:1 mint), so the 2× over-mint and ~$83k extraction arise **solely** from the in-flight accounting gap. Distinct root cause (TVL *completeness* vs *scale*) and distinct fix (track pending in-flight value / settlement callback vs normalize decimals). See `../DEDUP_MAP.md`.

> **Relationship to report #1 (ZEROMARK-1, the async-window report).** This finding addresses the *same* asynchronous deploy/recall window as the program's report #1 and is submitted on that basis — it is **not** claimed as novel relative to #1. The distinctness argued above is **solely** versus the decimal-scale bug ZEROMARK-553 (which is a different root cause, opposite error direction, and disjoint fix — see `../CARTHA-SEAM-001/DISPUTE_not_dup_of_async.md`).

## Summary

Deploying vault USDC into a 0xMarkets pool is a **two-step asynchronous** operation: `deployToPool()` sends USDC to the 0xM deposit vault immediately, but GM tokens are minted to the Cartha vault only later, by a **separate 0xMarkets keeper transaction**. During that window the vault holds *neither* the USDC (sent out) *nor* the GM (not yet minted), and `_totalValueLocked()` counts the in-flight amount in neither leg — so TVL is **understated** by the deployed amount. Anyone who deposits in that window is **over-minted** shares (`assets * totalSupply / understatedTVL`) and permanently captures value from existing holders. The recall path has the symmetric defect (GM sent out before USDC returns).

This is independent of CARTHA-SEAM-001: it occurs even when GM is valued correctly (the PoC uses a correct-valuation configuration to isolate it).

## Vulnerability detail

`PoolDeployLib.deploy` moves USDC out before any GM exists, with no callback to record the in-flight amount:

```solidity
IExchangeRouter(router).sendTokens(asset, depositVault, amount);   // USDC leaves the vault NOW
...
createDeposit(... receiver: address(this), callbackContract: address(0), callbackGasLimit: 0 ...);
// GM is minted to the vault LATER, by the 0xM keeper, in a separate tx. No callback updates Cartha.
```

TVL is computed purely from current balances; the pending deposit is invisible:

```solidity
function _totalValueLocked() internal view returns (uint256) {
    return IERC20($.asset).balanceOf(address(this)) /* dropped by `amount` */
         + _gmValueInUsdc($);                        /* GM not minted yet => 0 for this tranche */
}
```

`deployToPool` does not record the in-flight amount (the `deployedGmBalance` storage field is unused), and `_convertToShares` divides by the understated TVL:

```solidity
return (assets * totalShares) / totalAssets_;   // totalAssets_ understated during the window => over-mint
```

The error compounds to the parent: `CarthaParentVault.totalAssets()` reads `child.totalValueLocked()`, so a deposit into the parent during a child's deploy window over-mints parent shares too.

## Impact

A depositor who lands a transaction in the deploy window mints shares at an artificially low price and keeps the excess permanently (the lock period only delays withdrawal; the share-count gain is fixed at deposit time and is PnL-neutral relative to other holders). The over-mint multiple is `1 / (1 - deployRatio)` — e.g. a keeper deploying 50% of TVL lets a window-depositor mint **2×** the fair shares, extracting ~that much from existing LPs on withdrawal. Honest depositors who happen to transact in the window are also mispriced; redeemers in a recall window are underpaid.

## Step-by-step (from the PoC, GM valued correctly to isolate the bug)

1. Incumbent LP deposits **$1,000,000**; `totalValueLocked() == $1,000,000`.
2. Keeper calls `deployToPool(500_000e6)` and does **not** yet execute the 0xM deposit. Window open: `totalValueLocked()` drops to **$500,000** while $500k is in-flight (true value still $1M).
3. Attacker deposits **$100,000** in the window → minted **2e23** shares vs the fair **1e23** (exactly 2× at a 50% deploy).
4. 0xM keeper executes the pending deposit → GM minted, TVL restored.
5. A control user depositing the same $100k *after* settle gets only `~1.09e23` shares.
6. After lock+cooldown the attacker `release()`s and withdraws **$183,333** on a $100,000 deposit — ~$83k extracted from the incumbent.

```
fair shares for $100k       : 100000000000000000000000
attacker shares (in-window) : 200000000000000000000000   <-- 2x over-mint
control  shares (post-settle): 109090909090909090909090
attacker deposited (USDC): 100000000000   withdrew: 183333333333
```

## Recommended fix

Track in-flight value so TVL is continuous across the async window:
- On `deployToPool`, record the sent USDC as `pendingDepositUsdc`; clear it when the GM is observed (or on cancellation refund). Count `pendingDepositUsdc` in `_totalValueLocked()`.
- On `recallFromPool`, record the GM value sent out as `pendingWithdrawalValue` and count it until USDC returns.
- Alternatively, register a 0xM deposit/withdrawal **callback** (`callbackContract`) so settlement updates accounting atomically, and/or pause deposits/redemptions while a deploy/recall is pending for the vault.

## Re-verification note

Re-verified with the project's Foundry harness. To isolate this from CARTHA-SEAM-001, the GM token is valued correctly (default 1:1 mock mint + `setMarketTokenPrice(1e30)` ⇒ `gmValueInUsdc` returns the true USD value), so the 2× over-mint and the $83k extraction arise **solely** from the in-flight accounting gap. Test passes.
