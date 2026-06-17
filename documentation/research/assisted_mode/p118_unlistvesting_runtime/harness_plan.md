# P118 — Harness plan

**Classification: HARNESS_MODERATE.** secondswap ships a working Foundry env (lib/forge-std + a hardhat/console shim;
it ran live in P109). Reuse the existing M-11 PoC setup pattern.

## Required contracts (all REAL, from secondswap src)
SecondSwap_Marketplace (function under test), SecondSwap_VestingManager, SecondSwap_MarketplaceSetting,
SecondSwap_StepVesting + two mock ERC20s (vesting token, currency).

## Actors
`holder` (seller), `attacker` (non-seller/non-admin), `admin` (== s2Admin), `tokenIssuer`, `feeCollector`.

## Setup steps (mirror M-11)
deploy tokens → VestingManager.initialize(admin) → MarketplaceSetting(feeCollector,admin,whitelistDeployer,vmgr,
currency) → Marketplace.initialize(currency,setting) → vmgr.setMarketplace(mkt) → StepVesting(manager=vmgr) →
vmgr.setSellable(sv,true) → fund + createVesting(holder, A) → mint+approve currency → `holder` lists via
`mkt.listVesting(sv, amount, PRICE, 0, PARTIAL, NO, 0, currency, 0, false)`.

## Test cases
- A: `attacker` calls `unlistVesting` → expect revert "Not the seller".
- B: `holder` unlists (warp past minListingDuration=120 to skip the penalty branch) → ok; second unlist → expect
  revert "Listing not active" (no double-return).
- C: positive control — `holder` unlists own listing once → succeeds.
- D: `admin` (s2Admin) unlists → succeeds (intended privileged branch).

## Missing dependencies
None — secondswap lib provides forge-std + OZ + hardhat console shim. (State change asserted via revert behavior; the
13-field Listing tuple is NOT destructured to avoid stack-too-deep.)

## Project location
`/tmp/p97-secondswap/test/audit/UnlistVestingRuntime.t.sol`. secondswap `contracts/` (src) unmutated.
