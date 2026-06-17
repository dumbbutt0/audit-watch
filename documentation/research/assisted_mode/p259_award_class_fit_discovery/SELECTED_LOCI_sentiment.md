# sentiment — Phase 2: Selected loci + no-hindsight locks (PRE-REVEAL) — CONTAMINATED-DISCLOSED
3 subtle loci. **#541 area + max*/preview* excluded.**
## S-L1 `PositionManager.liquidate` / `_transferAssetsToLiquidator`
- why: liquidation seizure-vs-repay boundary = classic lending value transfer.
- signal: ST on liquidate/_transferAssetsToLiquidator; accounting on repay.
- what base knew: liquidator-supplied assetData seizure + debt repay + health check.
- what remained incomplete: can liquidator over-seize / seize healthy / mis-price collateral.
- why subtle: solvency boundary + identity (liquidator vs owner), not mechanical.
## S-L2 `Pool.rebalanceBadDebt`
- why: bad-debt socialization accounting across depositors.
- signal: accounting A4 on rebalanceBadDebt.
- what base knew: bad debt written down to lenders.
- what remained incomplete: who absorbs / double-count / interaction with shares.
- why subtle: solvency accounting.
## S-L3 `SuperPool.reorderDepositQueue`/`reorderWithdrawQueue`
- why: queue order drives allocation/withdrawal across pools.
- signal: ST on reorder queues.
- what base knew: owner reorders queues.
- what remained incomplete: ordering manipulation → deposit/withdraw to favored pool / liveness.
- why subtle: state-machine allocation.
**FREEZE.**
