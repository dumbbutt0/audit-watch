# EA-001 — Share dilution via deposits during the async 0xM (GMX-v2) deploy/recall window — in-flight value omitted from TVL

> **DISPOSITION: MERGED — duplicate.** This is the same root cause as another finding; it is kept here for traceability only and should NOT be submitted separately (see Triage reasoning for the primary).

- **Severity (recommended):** High
- **Category (HackenProof VRT):** Transaction-Ordering Dependence (TOD) / Front Running
- **Triage status:** merged
- **Confidence:** High
- **ICE:** Impact=High · Confidence=High · Exploitability=Permissionless (conditional on front-running / back-running a keeper deploy or recall before the 0xM keeper executes — a multi-block but publicly observable window)
- **Location(s):** `src/CarthaVault.sol:476-508,938-945,912-933; src/libraries/PoolDeployLib.sol:33-34,42-58,61-71,97-109`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`, `PoolDeployLib.sol`

## Description

CONFIRMS DT-001 from source, end-to-end. _totalValueLocked() (CarthaVault.sol:938-941) = IERC20(asset).balanceOf(this) + _gmValueInUsdc(). _gmValueInUsdc() => PoolDeployLib.gmValueInUsdc (PoolDeployLib.sol:97-109) reads gmBalance = IERC20(poolToken).balanceOf(this), i.e. GM tokens the vault PHYSICALLY HOLDS right now. deployToPool() (CarthaVault.sol:476-508) calls PoolDeployLib.deploy() which executes IExchangeRouter.sendTokens(asset, depositVault, amount) (PoolDeployLib.sol:34) — USDC leaves the vault to the 0xM depositVault IMMEDIATELY in the deploy tx — then createDeposit(...) with callbackContract=address(0), callbackGasLimit=0 (PoolDeployLib.sol:42-58), which only QUEUES a deposit request in the GMX-v2 fork. GM is minted to receiver=address(this) by a SEPARATE 0xM keeper transaction (executeDeposit) in a LATER block. Between the deploy tx and the keeper-execution tx the vault holds NEITHER the USDC (sent out) NOR the GM (not yet minted), so _totalValueLocked() undercounts by exactly `amount`. The storage field deployedGmBalance (CarthaVault.sol:74) that could track in-flight value is never written — confirmed: grep shows it is read only by the view deployedGmBalance() which returns _gmValueInUsdc($), not the in-flight amount.

During the window, _convertToShares(D) = D * totalSupply / TVL (CarthaVault.sol:912-922). With TVL understated, the denominator is too small, so a window depositor (depositAndLock / depositFromParent) is over-minted shares. When the 0xM keeper settles, GM appears, TVL is restored to its true value, and the window-depositor keeps a permanently inflated share count that now represents a larger fraction of the (now-correct) TVL — value silently transferred from pre-existing holders. The symmetric defect exists for recallFromPool() (CarthaVault.sol:513-531 -> PoolDeployLib.recall sends GM out at line 71 before USDC returns in a later keeper tx): during the recall window TVL is OVER-counted relative to assets actually present? No — recall sends GM out so _gmValueInUsdc drops immediately while USDC has not yet returned, so TVL is UNDER-counted again, meaning a redeemer in the recall window is UNDERPAID and a depositor in the recall window is again over-minted. Either async leg understates TVL.

## Impact

Permissionless value transfer from existing depositors to anyone who deposits while a keeper deploy/recall is in flight. Quantified (partial deploy): vault holds 500,000 USDC idle + 500,000 USDC of GM (totalSupply S, TVL = 1,000,000e6). Keeper calls deployToPool(500,000e6). In the deploy tx USDC.balanceOf(vault) drops to ~0 and GM has not yet been minted, so during the window TVL_window = 0 + 500,000e6 = 500,000e6 (only the PRE-EXISTING GM is counted). An attacker deposits D = 100,000e6 (>= DEFAULT_MINIMUM_LOCK_AMOUNT). shares_attacker = D * S / TVL_window = 100,000e6 * S / 500,000e6 = 0.2*S. Honest value: at true TVL 1,000,000e6 the same deposit should mint 100,000e6 * S / 1,000,000e6 = 0.1*S. The attacker receives 2x the shares they should, i.e. ~+100% extra. After the keeper settles, TVL returns to 1,000,000e6 + 100,000e6(attacker USDC) = 1,100,000e6 backing (S + 0.2S) shares; the attacker's 0.2S of (1.2S) = 16.67% of the pool now claims 16.67% * 1,100,000e6 = ~183,333e6 against a 100,000e6 deposit — a free ~83,333 USDC drawn pro-rata from the other holders (capped in practice by vault idle/recall liquidity at release time). If the keeper deploys 100% of TVL the window TVL collapses toward the residual idle, and the over-mint multiple grows without bound (1/(1-deployRatio)). maxDeployRatioBps caps deployRatio but the cap (default unset / can be up to 10000) is enforced on the POST-deploy ratio using the same understated TVL, so it does not prevent the window.

## Attack path (Intent / Technique / Evasion)

- **Intent:** A permissionless depositor steals a share of existing CarthaVault / CarthaParentVault holders' principal+PnL by minting shares while reported TVL is artificially deflated during the async 0xM settlement window.
- **Technique:** 1) Watch the public mempool for the KEEPER_BOT deployToPool(amount, ...) tx (or recallFromPool). 2) In the same block (after the deploy tx) or any block before the 0xM keeper's executeDeposit lands, call depositAndLock(poolId, D, lockDays) with D >= minimumLockAmount; _convertToShares uses the deflated _totalValueLocked() and over-mints shares = D*totalSupply/TVL_window. 3) Wait out lockDays + cooldown (delay only — the inflated share COUNT is fixed at deposit time). 4) release()/requestRelease(): _convertToAssets(shares) = shares*TVL/totalSupply pays out the inflated fraction of the now-correct TVL, extracting the surplus from other holders.
- **Evasion:** No privileged role and no special token needed — the normal whenNotPaused deposit path. The developer's intended TVL accounting (_totalValueLocked = idle USDC + held GM) silently fails to count in-flight value because GMX-v2 deposits are asynchronous (createDeposit only queues; callbackContract=address(0) means there is no callback to mark funds in-flight). The lock period is NOT a defense: it delays realisation but the share-count advantage is PnL-neutral and locked in at deposit; the maxDeployRatioBps cap is computed against the same understated TVL so it cannot close the window.

## Reachability / follow-up

merged into DT-001.

## Triage reasoning

Duplicate of DT-001 (async deploy/recall window share dilution), independently re-derived by the economic_attack pass which also quantified it (over-mint multiple = 1/(1-deployRatio)). Merged into DT-001.
