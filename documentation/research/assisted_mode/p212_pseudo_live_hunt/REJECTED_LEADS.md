# P212 — rejected leads (source-refuted by blind subagents)

| lead | surface | why rejected |
|---|---|---|
| deposit BoostTooHigh underflow | sf-01 | L581-583 guard reverts if _boostAmount > _depositAmount |
| reentrancy on deposit/withdraw | sf-01/02/04 | state written before transfer; LSTs (wstETH/weETH/sDAI) not ERC-777; no untrusted callee |
| over-withdraw beyond deposit | sf-02 | L713-717 cap / revert WithdrawTooHigh |
| aggregate boost > deposit | sf-03 | cap=depositAmount shrinks monotonically each call |
| stale accrual on setter changes | sf-07 | setEndBlock/setPointsPerBlock/setBoosterMultiplier call massUpdatePools first |
| setStartBlock retroactive | sf-07 | reverts FarmingIsStarted once started |
| boosterMultiplier<1e18 | sf-07 | reverts InvalidBooster |
| initialize permissionless front-run | sf-08 | onlyOwner modifier |
| withdrawProceeds steals user principal | sf-08 | heldProceeds incremented only by boosts; depositAmount tracked separately |
| proxy upgrade hijack | sf-08 | 2-step guards compose (onlyOwner sets pending; only pending accepts) |
| poolExists dup bypass | sf-06 | guard set before push, checked on add |
