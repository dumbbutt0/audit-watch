# Submission draft — Shared-position fee accounting in `ILOPool.claim` lets the first claimant divert other investors' fees and locks later claims

> **STATUS: PLATFORM-NEUTRAL DRAFT — NOT FINAL, DO NOT SUBMIT.**
> Platform-specific framing (severity-tier mapping, program-rule wording, disclosure format) and the final
> title are intentionally omitted until a human verifies (a) the program's scope/rules and (b) duplicate /
> publicly-known status. This draft is grounded only in the in-scope source and an executable test. See
> `pre_submission_gate.md` for the open human checks.

## Summary
An `ILOPool` wraps a **single** Uniswap V3 liquidity position, and every investor/project NFT is an internal
accounting *share* of that one shared position. `claim()` collects the **entire** shared position's accrued
fees (`collect(…, max, max)`), pays the calling NFT only its own share, and forwards the **residual — which
contains every other investor's accrued fees — to `feeTaker`**. Because the other NFTs' fee checkpoints are
never updated, a later claimant still computes its full historical fee entitlement against tokens the contract
no longer holds. The result: the first claimant's transaction diverts the other investors' fees to `feeTaker`,
and once accrued fees are non-trivial, **later `claim()` calls revert**, locking those investors out of their
vested position.

## Affected code
- `src/ILOPool.sol` — `claim()` (≈ L184–261).
- Supporting: `src/ILOPool.sol` `launch()` (≈ L269–335, mints the single shared position via `addLiquidity`),
  `buy()` (≈ L126–176, where per-NFT positions are created without fee checkpoints).

## Vulnerability details
1. **One shared Uniswap position, many internal shares.** `launch()` calls `addLiquidity(...)` once
   (≈ L296–303), minting a single `(owner = ILOPool, TICK_LOWER, TICK_UPPER)` Uniswap V3 position holding the
   whole ILO liquidity. Each investor/project NFT is tracked only as an internal share
   (`_positions[tokenId].liquidity`, `.feeGrowthInside0/1LastX128`), defaulting to `0` and not initialized
   with the position's fee growth in `buy()`/`launch()`.
2. **`claim()` collects the whole position's fees.** In `claim()`:
   - `pool.burn(TICK_LOWER, TICK_UPPER, liquidity2Claim)` (≈ L205). In Uniswap V3, `burn` runs
     `_updatePosition`, which credits **all** accrued swap fees for the position's *entire current liquidity*
     (i.e. every investor's share) into the position's `tokensOwed0/1`.
   - `pool.collect(address(this), TICK_LOWER, TICK_UPPER, type(uint128).max, type(uint128).max)` (≈ L242–248)
     then pulls the **whole** owed balance — the claimant's burned principal **plus all investors' accrued
     fees** — into the `ILOPool` contract.
3. **Only the claimant's share is paid; the rest goes to `feeTaker`.** The contract computes the calling NFT's
   own amount (post-platform-fee principal + that NFT's pro-rata fees, ≈ L214–231) and transfers it to the
   claimant (≈ L252–253). It then sends the **residual** `amountCollected − amountPaid` — which contains the
   other investors' accrued fees — to `feeTaker` (≈ L259–260).

## Root cause
`claim()` treats a per-investor action as if it owned the entire shared position: it collects fees for the
full position (`collect(max, max)`) but only accounts for the caller's share, with no mechanism to leave the
remaining investors' fees in the pool or to credit them internally. The other NFTs' `feeGrowthInside…Last`
checkpoints are never advanced, so their later fee computation references fees that were already swept out.

## Failure / attack scenario (no privileged setup)
1. Two or more investors `buy()` into an ILO; the project `launch()`es, deploying the single shared position.
2. Normal trading accrues swap fees on the pool.
3. Investor A calls `claim()` first (an ordinary, unprivileged action). A receives A's share; the accrued fees
   belonging to the other investors are routed to `feeTaker`.
4. Investor B calls `claim()`:
   - If accrued fees are small (within the platform-fee buffer), B is silently **under-paid**.
   - Once accrued fees exceed that buffer, B's `claim()` **reverts** — B cannot withdraw the vested position
     at all.

No malicious actor is required: *any* ordering harms whoever claims later. An attacker who simply claims first
(or front-runs) deterministically diverts the others' fees and can grief later claimants into a revert.

## Impact
- Investors other than the first claimant **lose their share of accrued Uniswap fees** (diverted to
  `feeTaker`).
- Once accrued fees are material, later claimants **cannot claim their vested liquidity** — `claim()` reverts,
  and the position's funds are stranded for those investors.

## Proof of concept
An executable Foundry test reproduces the defect against the in-scope source. It encodes the invariant that
holds on correct code — *a position's claim proceeds are independent of whether another investor claimed
first* — using `vm.snapshot`/`vm.revertTo` to compare the two orderings at the same unlock and price:
- Two investors buy in and the ILO is launched; realistic swap volume accrues fees on the shared position.
- **Scenario A:** investor 2 claims first → receives ~15,151 USDC.
- **Scenario B:** investor 1 claims first, then investor 2 claims the same position → investor 2's claim
  **reverts and receives 0**.

### Steps
1. Clone the in-scope repo at the pinned commit (see `evidence_bundle.md`) and `git submodule update --init`.
2. Place the PoC test in the project's `test/` directory.
3. Run the test command below.

### Test command
```
forge test --match-test testH01_ClaimProceedsAreOrderIndependent -vv
```

### Actual vs expected
- **Expected (correct code):** investor 2 receives the same amount and does not revert regardless of claim
  order.
- **Actual (current source):** the test **fails** — investor 2 receives ~15,151 USDC when claiming first but
  **reverts and receives 0** when claiming after investor 1 (whose claim swept the shared fees to `feeTaker`).

## Recommended mitigation
`claim()` must not remove other investors' fees from the position. Either:
- Collect only the amount this claim distributes — e.g. collect the claimant's principal + the claimant's
  pro-rata fees rather than `collect(…, type(uint128).max, type(uint128).max)`, leaving the remaining
  investors' fees in the Uniswap position; **or**
- Account fees internally per NFT (advance each NFT's `feeGrowthInside…Last`) so a global collect cannot
  over-distribute another investor's entitlement.

A minimal change of the first kind (collecting only the per-claim amounts instead of the position maximum)
makes the order-independence invariant hold in the PoC; see `evidence_bundle.md`. The production fix must also
preserve correct platform/performance-fee routing and is left to the maintainers.

## Assumptions
- Fees accrue on the shared Uniswap position between launch and claim (normal trading); the PoC uses realistic
  swap volume to bring accrued fees above the platform-fee buffer so the revert manifests. Below that buffer
  the same root cause produces silent under-payment rather than a revert — both regimes stem from the same
  accounting flaw.
- The PoC deploys the in-scope contracts locally and forks mainnet only for stable, standard dependencies
  (Uniswap V3 factory, WETH9, USDC); no protocol state is assumed beyond what `launch()`/`buy()` create.
- No privileged role or special configuration is required to trigger the issue.
