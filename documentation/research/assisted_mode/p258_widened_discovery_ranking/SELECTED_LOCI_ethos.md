# ethos — Phase 2: Selected loci + no-hindsight locks (PRE-REVEAL)

3 subtle loci (BASE_BORN_INCOMPLETE; ≥2 mechanisms; multi-family).

## E-L1 `ActivePool._rebalance` (Ethos-specific collateral→ERC4626 yield)
- why selected: the Ethos-unique twist on Liquity; ERC4626 conversion + profit accounting = highest novel risk.
- base signal: accounting A4/A2 on _rebalance/sendCollateral.
- checkpoint signal: accounting shared-balance-depletion cluster.
- what base knew: profit = convertToAssets − yieldingAmount; netAssetMovement deposit/withdraw; profit recalc.
- what remained incomplete: ERC4626 share/asset conversion mismatch or profit miscalc → loss/insolvency.
- expected subtle class: convexity (B) / migration-conversion (E) / accounting (A) / temporal (G).
- why not trivial: ≥4 family mechanisms.

## E-L2 `StabilityPool.offset` (P/S product reward)
- why selected: Liquity compounding-stake math is a classic subtle drift surface.
- base signal: accounting A on offset.
- checkpoint signal: accounting on offset.
- what base knew: P (product) and S (sum) snapshots, scale/epoch.
- what remained incomplete: scale/epoch snapshot drift or rounding in compounded deposits.
- expected subtle class: temporal/epoch (G) / accounting (A) / convexity (B).
- why not trivial: ≥3 mechanisms.

## E-L3 `RedemptionHelper.redeemCollateral` + `SortedTroves.reInsert`
- why selected: redemption ordering + partial-redemption reinsert is a state-machine + identity surface.
- base signal: ST on redeemCollateral/reInsert.
- checkpoint signal: ST dual-state + reset on reInsert.
- what base knew: redemption walks troves ascending, partial redemption reinserts.
- what remained incomplete: ordering/hint manipulation or redeemer-vs-owner identity.
- expected subtle class: state-machine (C) / identity (F) / temporal (G).
- why not trivial: ≥3 mechanisms.

**FREEZE:** final before enumeration/reveal.
