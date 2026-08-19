# DT-001 — Share dilution via deposits during the async 0xM pool deploy/recall window (in-flight value not counted in TVL)

- **Severity (recommended):** High
- **Category (HackenProof VRT):** Transaction-Ordering Dependence (TOD) / Front Running
- **Triage status:** poc_required
- **Confidence:** High
- **ICE:** Impact=High · Confidence=High · Exploitability=Permissionless (conditional on catching a keeper deploy in-flight)
- **Location(s):** `src/libraries/PoolDeployLib.sol:33-34,61-71; src/CarthaVault.sol:476-531,938-945,912-933`
- **Vulnerable files (bundled in `sources/`):** `PoolDeployLib.sol`, `CarthaVault.sol`

## Description

CarthaVault._totalValueLocked() = asset.balanceOf(vault) + gmValueInUsdc(). deployToPool() sends USDC to the 0xM depositVault (PoolDeployLib.deploy -> ExchangeRouter.sendTokens) immediately, but GM tokens are only minted later by a 0xM keeper in a separate transaction (createDeposit queues the request; receiver=vault, no callback). During that window the in-flight USDC is counted by neither leg, so TVL is understated by the deployed amount. _convertToShares(D) = D*totalSupply/TVL therefore over-mints to anyone depositing in the window (depositAndLock / depositFromParent / depositAndLockSpread). When the deposit settles, TVL is restored and the window-depositor keeps a permanently inflated share count, extracting value from existing holders after the lock+cooldown. recallFromPool() has the symmetric defect (GM leaves before USDC returns -> redeemers underpaid). The error also propagates to the parent because CarthaParentVault.totalAssets() reads child.totalValueLocked(). There is no in-flight accounting (the deployedGmBalance storage field is unused).

## Impact

Permissionless value transfer from existing depositors to a depositor who times the async window; magnitude scales with the deployed fraction of TVL (a 50% deploy ~doubles the window-depositor's share count). Honest depositors/redeemers are also mispriced.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Extract value from existing vault holders by minting shares while the vault's reported TVL is artificially low.
- **Technique:** Observe the public KEEPER deployToPool tx; deposit >= minimumLockAmount during the window before the 0xM keeper mints GM; _convertToShares over-mints; wait out lock+cooldown then release the inflated share value.
- **Evasion:** No special privileges; uses the normal permissionless deposit path. The lock period only delays (does not prevent) realisation; the share-count gain is locked in at deposit time and is PnL-neutral relative to other holders.

## Reachability / follow-up

reachable: yes — observe the public deployToPool tx, deposit >= 100k USDC before the 0xM keeper executes. no_privileged_keys: attacker uses permissionless depositAndLock. state_before_after: idle drops by `amount` on deploy, GM not yet minted -> TVL understated by `amount` -> over-mint -> TVL restored on settle, excess shares retained. why_guards_fail: no in-flight accounting (deployedGmBalance unused); maxDeployRatioBps computed against the same understated TVL. scope_match: core.

## Triage reasoning

Async pool deploy/recall window dilution. deployToPool sends USDC to the 0xM depositVault immediately (PoolDeployLib.deploy -> sendTokens) but GM is minted only later by a separate 0xM keeper tx (createDeposit queues; no callback). During the window the in-flight USDC is counted by neither leg of _totalValueLocked, so it is understated and _convertToShares over-mints to depositors in the window; recallFromPool is the symmetric leg. The share-count gain is locked in at deposit time (lock only delays realisation). Propagates to the parent via totalAssets() reading child.totalValueLocked(). Distinct from CARTHA-SEAM-001: this is the transient in-flight gap (independent of the decimal bug). Merges EA-001 (duplicate of this from the economic_attack pass).
