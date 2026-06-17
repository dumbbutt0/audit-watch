# P207 — H-01 positive control (HIGH_CONFIRMED, executed)

Harness: `pocs/p207/test/H01_claimFees.t.sol` + `FaithfulV3Pool.sol` (solc 0.7.6, forge 1.5.1). Real `ILOPool`
(byte-identical `realsrc/`, cloned), real `ILOManager` interface via `ManagerStub`.

## Mechanism executed
All ILO investors share ONE Uniswap-V3 position owned by the `ILOPool`. In `claim()`:
1. `pool.burn(TICK_LOWER,TICK_UPPER,liq)` **pokes the whole position**, crediting ALL accrued fees to `tokensOwed`.
2. `pool.collect(…, max, max)` pulls the entire position's owed tokens into `ILOPool`.
3. `ILOPool` pays the claimer their computed share and **routes `amountCollected − amount` (the other investors'
   fees) to the `feeTaker`**.

So the **first** claimer's transaction drains every investor's fees; a **later** claimer's `collect` returns only
principal, but `ILOPool` still computes their fee entitlement from `feeGrowthInside` → the payout exceeds the
contract's balance / `amountCollected − amount` underflows → **their claim reverts** and their fees are already gone.

## Executed result (`forge test`, 2/2 pass)
Setup: A buys 60e18, B buys 40e18 (share one position); `launch()`; real swap accrues 100e18 token0 fees; vest.
- **A (first) `claim()`** → receives **120e18** (60e18 principal + 60e18 *fair* fee share).
- **L2 state flip:** `feeTaker` balance = **40e18** = B's rightful fee share, siphoned on A's claim
  (`assertEq(feeTaker, 40 ether)`).
- **L3 outcome:** **B's `claim()` REVERTS** (`expectRevert`) — B, a legitimate position holder, can no longer claim;
  their fees are lost and principal is locked = **material fund loss**.
- **Control (`test_H01_control_single_investor_claims_ok`):** a sole investor claims fine, receives 200e18
  (principal + ALL fees), feeTaker = 0 → the defect requires multi-user fee commingling, **it is not an artifact of
  the pool mock**.

## Faithfulness of the V3 pool model (why this is not a rigged mock)
`FaithfulV3Pool` implements canonical single-position V3 accounting: `burn` pokes the **whole** position
(`tokensOwed += (feeGrowthInside − posLast)·liquidity / Q128`) and advances `posLast`; `collect` pays `min(owed,max)`;
`accrueFees` raises `feeGrowthInside` by `fee·Q128/liquidity` and mints the fee tokens to the pool (real swap-accrued
fees). The mock contains **no per-user logic and no bug** — the loss arises entirely from `ILOPool`'s own
cross-user fee accounting and its `collect(max)`/feeTaker routing. The control test confirms a single holder is made
whole, isolating the defect to ILOPool.

## L3 verdict
`HIGH_CONFIRMED` — permissionless, source-valid config, honest custody, executed material fund loss with named
before/after balances. Preserves the awarded High on a 2nd corpus.
