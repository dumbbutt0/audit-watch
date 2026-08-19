# DOS-001 — One child vault's reverting GM price read bricks ALL parent operations (parent `totalAssets()` has no per-child try/catch)

| | |
|---|---|
| **Severity** | **High** (protocol-wide freeze of every parent LP's deposits *and* withdrawals; one bad child poisons the whole pool) |
| **Category (HackenProof VRT)** | DoS with (Unexpected) revert |
| **Target** | Cartha Vaults (`cartha-vaults-main`, commit `4c51f2a8915f438976b57134d646b55199a11318`) |
| **Contracts** | `src/CarthaParentVault.sol`, `src/CarthaVault.sol`, `src/libraries/PoolDeployLib.sol` |
| **Trigger** | Any condition under which **one** child's GM price read reverts — a real, reachable 0xMarkets state (stale/empty oracle price, disabled market, pool-value edge), **not** an attacker-forced action. |
| **Impact scope** | All LPs of the parent (every child), plus the affected child's own miners. Funds frozen (not stolen) until the single child's read recovers. |
| **PoC** | `poc/PoC_ParentBrickOnChildRevert.t.sol` (self-contained, passing — `poc/run_output.txt`) · **Integrated:** `poc_integrated/` deploys the **real in-scope 0xMarkets `Oracle`** and proves the genuine `EmptyPrimaryPrice` revert surfaces verbatim at `parentVault.totalAssets()` (passing — `poc_integrated/run_output.txt`) |

## Not a duplicate of CARTHA-SEAM-001 (already reported) or DT-001

This is a **liveness / fault-isolation** bug, independent of both other Cartha findings and surviving both their fixes:
- **vs CARTHA-SEAM-001** (GM decimal scale): SEAM is about the *value* the GM read returns; DOS-001 is about the read *reverting*. In the PoC the GM is valued **correctly** (1:1 mint + `1e30` reader price), and the freeze still occurs — it comes purely from the missing `try/catch` around the cross-child external call (`CarthaParentVault.sol:356`), regardless of GM scale.
- **vs DT-001** (async in-flight window): DT-001 is a share-price accounting gap while both legs are readable and nothing reverts; DOS-001 is a hard revert in the pricing path. Different root cause, different fix.

## Summary

`CarthaParentVault.totalAssets()` sums each child's value by looping over `vaultList` and calling `child.totalValueLocked()` **with no `try/catch`**:

```solidity
// src/CarthaParentVault.sol:348-365
function totalAssets() public view returns (uint256 total) {
    ParentVaultStorage storage $ = _getParentVaultStorage();
    for (uint256 i = 0; i < $.vaultList.length; i++) {
        address vault = $.vaultList[i];
        if ($.pools[vault].isActive) {
            uint256 parentShares    = IERC20(vault).balanceOf(address(this));
            uint256 childTotalSupply = IERC20(vault).totalSupply();
            uint256 childTVL = ICarthaVault(vault).totalValueLocked();   // <-- no try/catch
            if (childTotalSupply > 0 && parentShares > 0) {
                total += (parentShares * childTVL) / childTotalSupply;
            }
        }
    }
    total += IERC20(asset()).balanceOf(address(this));
}
```

A child that holds GM prices it through an **unguarded chain of external calls** into the 0xMarkets fork. Any one of those reverting makes `child.totalValueLocked()` revert, which makes the parent's whole `totalAssets()` revert. Because **every** parent entry/exit path reads `totalAssets()`, a single child's reverting read freezes the **entire** parent — all deposits, all withdrawals, all releases, all force-exits — for every LP.

## Vulnerability detail

`child.totalValueLocked()` → `_gmValueInUsdc` → `PoolDeployLib.gmValueInUsdc` → `_getGmPrice` makes five external calls and guards only zero-balance / non-positive price — **it cannot guard a revert**:

```solidity
// src/libraries/PoolDeployLib.sol:97-127
function gmValueInUsdc(...) external view returns (uint256) {
    uint256 gmBalance = poolToken != address(0) ? IERC20(poolToken).balanceOf(address(this)) : 0;
    if (gmBalance == 0 || reader == address(0)) return 0;        // only zero-guards
    int256 gmPrice = _getGmPrice(reader, dataStore, market, oracle);
    if (gmPrice <= 0) return 0;                                  // only non-positive-guards
    return (gmBalance * uint256(gmPrice)) / GM_PRICE_PRECISION;
}
function _getGmPrice(...) private view returns (int256 gmPrice) {
    I0xMReader.MarketProps memory mkt = r.getMarket(dataStore, market);          // L119 — can revert
    I0xMReader.PriceProps memory indexPrice = o.getPrimaryPrice(mkt.indexToken); // L120 — can revert
    I0xMReader.PriceProps memory longPrice  = o.getPrimaryPrice(mkt.longToken);  // L121 — can revert
    I0xMReader.PriceProps memory shortPrice = o.getPrimaryPrice(mkt.shortToken); // L122 — can revert
    (gmPrice,) = r.getMarketTokenPrice(dataStore, mkt, indexPrice, longPrice, shortPrice, ...); // L124 — can revert
}
```

These reverts are **ordinary, reachable 0xMarkets states**, not contrived — confirmed directly in the in-scope 0xMarkets source:

| Revert | 0xMarkets source | When |
|---|---|---|
| `EmptyPrimaryPrice(token)` | `contracts/oracle/Oracle.sol:165` | no primary price set for the token in the current block (the common case for a view read outside an oracle-priced keeper tx) |
| `StaleOraclePrice(...)` | `contracts/error/Errors.sol:244` | stored price older than the allowed window |
| `DisabledMarket(market)` | `contracts/market/MarketUtils.sol:2660` | the GM market is disabled |
| `EmptyMarket()` / `EmptyMarketPrice(market)` | `contracts/market/MarketUtils.sol:2655`, `Errors.sol:439` | market not fully configured / empty |
| `UnableToGetCachedTokenPrice(token, market)` | `contracts/market/MarketUtils.sol:220` | `getMarketTokenPrice` can't resolve a constituent price |

`totalAssets()` is then consumed by `_convertToShares` / `_convertToSharesRoundUp` (deposit path), `_prepareSharePayout` (`CarthaParentVault.sol:456-470` — release/process/force-exit), and `sharePrice`. So the revert propagates to **every** parent user/keeper entrypoint:

```
child B GM read reverts (e.g. EmptyPrimaryPrice)
  → child.totalValueLocked() reverts                     (CarthaVault.sol:938-945)
  → parent.totalAssets() reverts (unguarded loop)        (CarthaParentVault.sol:356)
  → _convertToShares / _prepareSharePayout / sharePrice revert
  → depositAndLockSpread · lockAndSpread · lockTopUp · releaseFromParent
    · processQueuedParentWithdrawals · executeForceExit  ALL revert
```

The same revert also bricks the affected child's own `release()` / `requestRelease()` / `deployToPool()` (they read `_totalValueLocked()` via `_convertToAssets`). There is no per-child isolation and no fallback pricing.

## Impact

A **protocol-wide freeze**: while any single child's GM read reverts, no LP anywhere under the parent can deposit, withdraw, release, or be force-exited, and the affected child's miners cannot exit either. One pool's transient oracle condition (or a single misconfigured child added to the parent) takes down the entire parent for all users. Funds are not stolen but are **unwithdrawable** until the condition clears — which for a disabled/misconfigured market may be indefinite. This breaks the core availability invariant for every depositor, hence **High**.

> Honesty caveat: the trigger is an external 0xMarkets pricing-revert condition, not a primitive an attacker can force on demand (no permissionless attacker tx induces `EmptyPrimaryPrice`). A program that weights "requires an external precondition" may settle this at Medium. It is rated High here because the blast radius is every LP of the parent and the freeze is total (deposits *and* withdrawals), with no isolation. The *realism* of the trigger is not asserted on faith: the integrated PoC (`poc_integrated/`) deploys the **real in-scope 0xMarkets `Oracle`** and shows `getPrimaryPrice` on an unpriced token reverting the genuine `EmptyPrimaryPrice`, with that exact error selector surfacing verbatim at `parentVault.totalAssets()`.

## Step-by-step (from the PoC)

Two children under one parent (50/50). Child A holds plain idle USDC; child B is deployed into a 0xMarkets pool and holds GM. GM is valued **correctly** throughout (this is not the decimal bug).

1. Incumbent LP locks **$1,000,000** → $500k to each child. Keeper deploys $250k of child B into the pool; the 0xM keeper executes → **child B holds GM**.
2. **Baseline (healthy):** `parent.totalAssets() == $1,000,000`; the parent is fully operational. Incumbent queues a withdrawal (`requestReleaseFromParent`, which doesn't read TVL).
3. **Fault injected:** child B's GM read now reverts (modelled by pointing it at a `RevertingReader` standing in for `EmptyPrimaryPrice`/`DisabledMarket`/etc.).
4. **Every parent op now reverts** (each asserted with `expectRevert`):
   - `parent.totalAssets()` — pricing dead.
   - `parent.releaseFromParent(...)` — the locked incumbent **cannot exit**.
   - `parent.processQueuedParentWithdrawals([incumbent])` — the keeper's batch settlement **bricks**.
   - `parent.depositAndLockSpread(...)` — a new LP **cannot enter**.
5. **Isolation proof:** the healthy sibling child A's own `totalValueLocked()` still returns $500k — the failure is purely the parent's unguarded cross-child loop, not child A.
6. **Control (causation):** restore child B's reader → `parent.totalAssets()` returns $1,000,000 again and a real `releaseFromParent` succeeds, proving child B's revert was the sole cause.

```
healthy parent totalAssets() : 1000000000000   ($1,000,000)
healthy sibling child A TVL  : 500000000000     (child A fine on its own)
recovered parent totalAssets(): 1000000000000   (full recovery after reader restored)
incumbent partial exit (USDC) : 499999999999
```

## Recommended fix

Isolate each child's valuation so one reverting child cannot brick the parent:

```solidity
// Per-child try/catch in totalAssets(): skip (or floor) a child whose price read reverts,
// rather than reverting the whole aggregate.
try ICarthaVault(vault).totalValueLocked() returns (uint256 childTVL) {
    if (childTotalSupply > 0 && parentShares > 0) {
        total += (parentShares * childTVL) / childTotalSupply;
    }
} catch {
    // emit a degraded-pricing signal; treat this child's value conservatively (e.g. last-known
    // or idle-USDC-only) so the rest of the parent stays operational.
}
```

Additionally wrap the external read inside `PoolDeployLib._getGmPrice` in `try/catch` (or a staleness/empty guard) so a single pool's oracle hiccup degrades gracefully instead of reverting, and consider a keeper-set fallback/last-known GM price for valuation reads.

## Re-verification note

Re-verified end-to-end with the project's own Foundry harness (parent + 2 children via `CarthaVaultFactory`, real `depositAndLockSpread` / `deployToPool` / `releaseFromParent` flows). The GM is valued correctly in the healthy baseline (1:1 mock mint + `setMarketTokenPrice(1e30)`), so the freeze arises solely from the unguarded cross-child external call. The `RevertingReader` faithfully reproduces the 0xMarkets revert conditions cited above (it implements the same `I0xMReader` the production path calls; in production no contract swap is needed — the existing Reader reverts on its own under those states). All five brick assertions pass, and the control proves recovery. See `poc/run_output.txt`.

**Integrated re-verification with real 0xMarkets code (`poc_integrated/`).** To remove any doubt that the stand-in is faithful, a second PoC compiles the **real, in-scope 0xMarkets `Oracle`** (`contracts/oracle/Oracle.sol`, the GMX-v2 fork — RoleStore → DataStore → EventEmitter → Oracle, solc 0.8.24, no viaIR) and routes child B's pricing oracle to it. With no primary price set for the index token, the real `Oracle.getPrimaryPrice` reverts the genuine `Errors.EmptyPrimaryPrice`, and the headline assertion shows that **exact error selector** (`EmptyPrimaryPrice(indexToken)`) surfacing verbatim at `parentVault.totalAssets()` — the in-scope error reaches the parent boundary unguarded. The same brick/isolation/recovery assertions pass (2 tests). It lives in an isolated Foundry profile (`integration`, `test-integration/`) so the default build/CI never compiles 0xMarkets. Run: `FOUNDRY_PROFILE=integration forge test --match-path "test-integration/PoC_RealOxMOracleRevert_BricksParent.t.sol" -vv`. See `poc_integrated/README.md`.
