# DOS-001 — A single child vault whose GM price read reverts bricks ALL parent operations (totalAssets has no try/catch)

- **Severity (recommended):** High
- **Category (HackenProof VRT):** DoS with (Unexpected) revert
- **Triage status:** poc_required
- **Confidence:** High
- **ICE:** Impact=High · Confidence=High · Exploitability=Conditional (any child pricing-dependency revert; no privilege required to be hit, ADMIN-misconfig or oracle staleness suffices)
- **Location(s):** `src/CarthaParentVault.sol:348-365,456-470,557-562,625-704; src/CarthaVault.sol:280-337,938-945; src/libraries/PoolDeployLib.sol:97-127`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`, `CarthaVault.sol`, `PoolDeployLib.sol`

## Description

CarthaParentVault.totalAssets() (348-365) loops every active child and calls ICarthaVault(vault).totalValueLocked() with NO try/catch. totalValueLocked() -> _totalValueLocked() (CarthaVault:938-941) -> _gmValueInUsdc() -> PoolDeployLib.gmValueInUsdc() (97-127), which makes external 0xM-fork calls: reader.getMarket(), oracle.getPrimaryPrice() x3, reader.getMarketTokenPrice(). In a GMX-v2 fork these revert whenever the oracle has no fresh primary price for the index/long/short token in the current block, when the reader/datastore is mid-config, or when getMarketTokenPrice hits an arithmetic/empty-market edge. Because gmValueInUsdc only guards gmBalance==0 and gmPrice<=0 (it cannot guard a REVERT), one child whose GM read reverts makes the parent's totalAssets() revert. totalAssets() is consumed by _convertToShares, _convertToSharesRoundUp, _prepareSharePayout, sharePrice and therefore by every parent user/keeper entrypoint: lockAndSpread, depositAndLockSpread, lockTopUp, releaseFromParent, withdraw, requestReleaseFromParent->process, executeForceExit. So a transient or stuck oracle on ONE pool freezes deposits, withdrawals, releases and force-exits across the ENTIRE parent for all users — not just that pool. The same revert also bricks the affected child's own release()/requestRelease()/deployToPool() (all read _totalValueLocked via _convertToAssets). No pull-isolation and no fallback pricing exists.

## Impact

Protocol-wide withdrawal/deposit freeze for every parent depositor (and the affected child's miners) whenever any one child's GM oracle/reader call reverts. No attacker setup needed if the dependency is flaky; an ADMIN-misconfigured pricing seam on a single added child also triggers it. Funds are not stolen but become temporarily unwithdrawable across the whole parent until pricing is restored.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Freeze all parent deposits/withdrawals (and a child's releases) by making one child's GM price read revert.
- **Technique:** Any child added to the parent whose oracle/reader returns no price (stale block, unconfigured market, GMX getMarketTokenPrice edge) -> totalValueLocked() reverts -> totalAssets() reverts inside the unguarded vaultList loop -> _convertToShares/_prepareSharePayout/sharePrice revert -> every parent entrypoint reverts.
- **Evasion:** Developers guarded gmValueInUsdc against zero balance and non-positive price but not against the external calls themselves reverting; the parent loop has no per-child try/catch, so failure is not isolated to the bad pool.

## Reachability / follow-up

reachable: yes when any one child has a reverting GM price read (0xM oracle staleness/misconfig, or a wrong reader/market address). no_privileged_keys: the trigger is external oracle state, not an attacker tx, but the impact (frozen withdrawals) is borne by all users. state_before_after: one child reverts -> parent totalAssets reverts -> all parent ops revert. why_guards_fail: no per-child try/catch isolation. scope_match: core liveness.

## Triage reasoning

CarthaParentVault.totalAssets() loops vaultList calling child.totalValueLocked() -> PoolDeployLib.gmValueInUsdc() (external reader/oracle calls) with NO try/catch. If any one child's GM-price read reverts (stale/unconfigured 0xM oracle, gmPrice<=0 path returns 0 not revert — but a reverting getMarket/getPrimaryPrice DOES bubble), totalAssets() reverts, and every parent deposit/withdraw/release/force-exit consumes totalAssets() -> protocol-wide freeze. The same revert bricks that child's own release/requestRelease. Safety-net code (solvency aggregator) — NOT silently cleared; this is a confirmed liveness defect.
