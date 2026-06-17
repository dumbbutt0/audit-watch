# Reviewer notes — ILOPool.claim (H-01)

For the human triager. These notes argue the severity and pre-empt the obvious "is this real / is this just
rounding" objections, all from source + the executable test.

## Why this is High
Two distinct fund-impacting consequences, both reachable by an unprivileged user with no special setup:
1. **Direct value misallocation:** the first claimant's ordinary `claim()` routes every other investor's
   accrued Uniswap fees to `feeTaker` (residual transfer, ILOPool.sol ≈ L259–260). Those investors permanently
   lose fees they earned.
2. **Denial of vested funds:** once accrued fees exceed the platform-fee buffer, a later investor's `claim()`
   reverts (the contract no longer holds the tokens that NFT's accounting expects), so they **cannot withdraw
   their vested liquidity at all**. That is a loss/lock of principal-class funds, not merely lost yield.

Either consequence alone is a serious investor-fund issue; together, and triggerable permissionlessly by claim
ordering (or a front-run to guarantee being first), this sits in the High band. Final program-tier mapping is
left to the human (gate items 2–3).

## Why it is NOT dust / rounding
- The diverted amount is the **other investors' entire accrued fee balance** on the shared position, not a
  rounding remainder. In the PoC the affected amount is ~15,151 USDC for a single later claimant — and it
  scales with trading volume and number of co-investors.
- The second consequence is a hard **revert**, not an off-by-a-wei discrepancy: the later claim does not
  "round to zero," it fails outright and the funds stay locked.
- The minimal patch flips the outcome cleanly (pass ↔ fail), which a pure rounding artifact would not.

## Why later claimants lose fees or revert
The `ILOPool` holds **one** Uniswap V3 position shared by all NFTs. `claim()` does
`pool.collect(…, type(uint128).max, type(uint128).max)` (≈ L242–248), which pulls the whole position's owed
balance — including co-investors' fees — into the contract, pays the caller only its share (≈ L252–253), and
sends the rest to `feeTaker`. The other NFTs' `feeGrowthInside…Last` checkpoints (≈ L214–231) are never
advanced, so a later claimant still computes its full fee entitlement while the tokens are gone:
- if the shortfall is within the platform-fee buffer → silent under-payment;
- if it exceeds the buffer → the transfer math underflows/over-draws and the claim reverts.

## Why the minimal patch proves the root cause
Changing only the collect call from the position maximum to the per-claim amounts
(`collect(uint128(amount0), uint128(amount1))`) leaves co-investors' fees in the pool. With that one change the
order-independence invariant **passes** — investor 2 gets the same payout regardless of order, no revert. The
single-line locus of the fix isolates the defect to the over-broad `collect(max, max)` against a shared
position; nothing else in the test or environment changed. (This patch is a discriminator, not a vetted
production fix — the real fix must preserve correct platform/performance-fee routing.)

## What a triager should run
1. Pinned commit `befb1b1170`; `git submodule update --init --recursive`; `forge build` (solc 0.7.6).
2. If using the repo harness, point the `IntegrationTestBase` fork URL at any working mainnet RPC (the
   hard-coded ankr endpoint is now key-gated); a keyed archive RPC + pinned block gives full determinism.
3. Copy `H01ClaimFeeSiphon.t.sol` into `test/` and run:
   `forge test --match-test testH01_ClaimProceedsAreOrderIndependent -vv` → expect FAIL with investor 2
   getting ~15,151 USDC first vs REVERT/0 second.
4. (Optional) apply the minimal collect-scope patch and re-run → expect PASS; restore source.
5. Sanity: `forge test` full suite → 29/29 existing pass, only the PoC fails.

## Open items the triager owns (not resolved here)
- Confirm `ILOPool` and this impact class are in the program's scope.
- Check duplicate / publicly-known status against the program's known issues and prior reports.
- Decide the program severity tier and the final platform-specific wording before any submission.
