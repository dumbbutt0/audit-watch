# P212 — scope manifest (source-only, sophon)

## In-scope contracts
| contract | LOC | role |
|---|---|---|
| farm/SophonFarming.sol | 933 | core: deposits, boost, reward accounting, withdraw, (bridge=OOS), admin |
| farm/SophonFarmingState.sol | 92 | storage: PoolInfo/UserInfo structs, poolInfo[], userInfo, heldProceeds, boosterMultiplier, pointsPerBlock, start/endBlock |
| proxies/SophonFarmingProxy.sol | 14 | proxy entrypoint |
| proxies/Proxy2Step.sol | 24 | 2-step proxy impl swap |
| proxies/Upgradeable2Step.sol | 39 | 2-step ownership/upgrade base |

## External entry points (non-bridge, in-scope)
deposit · depositDai · depositStEth · depositeEth · depositEth(payable) · depositWeth · increaseBoost · withdraw ·
pendingPoints(view) · massUpdatePools · updatePool · poolLength/getPoolInfo/getOptimizedUserInfo (views) ·
withdrawProceeds(onlyOwner) · initialize(onlyOwner) · add/set(onlyOwner) · setStartBlock/setEndBlock/setPointsPerBlock/
setBoosterMultiplier(onlyOwner). **OOS:** bridgePool/revertFailedBridge/setBridge/setL2FarmForPool.

## Privileged roles
owner (onlyOwner: initialize/add/set/setStartBlock/setEndBlock/setPointsPerBlock/setBoosterMultiplier/withdrawProceeds);
proxy admin (2-step ownership in Upgradeable2Step).

## Asset custody points
deposit* (safeTransferFrom in) · withdraw (safeTransfer out, by user.depositAmount) · withdrawProceeds (owner pulls
heldProceeds) · predefined-pool conversions hold converted assets (sDAI/wstETH/weETH).

## Accounting / invariant surfaces
accPointsPerShare reward accrual (updatePool vs _pendingPoints scaling: updatePool L430 `pointReward/lpSupply`,
_pendingPoints L373 `pointReward*1e18/lpSupply`) · rewardDebt/rewardSettled per user · pool.amount = deposits +
boosted; user.amount likewise · boost: heldProceeds += boostAmount, boost*boosterMultiplier/1e18, deposit reduced by
boost · getMaxAdditionalBoost = depositAmount (100% cap) · withdraw reduces depositAmount & amount by withdrawAmount
(but boost portion of amount?) · units/decimals in predefined conversions + boost re-scale (boost*finalAmount/initalAmount).

## Upgrade/admin controls
2-step proxy (Proxy2Step/Upgradeable2Step); initialize gated whenNotInitialized-style; setEndBlock sets withdrawal window.

## Likely high-value attack surfaces
reward-accounting scaling mismatch; boost accounting conservation (pool.amount vs custody); withdraw vs boost interplay;
predefined-pool conversion units; admin param transitions (setEndBlock/setStartBlock after start) vs accrual; proxy
init/ownership.
