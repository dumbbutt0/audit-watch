# Evidence bundle — M-11 `maxSellPercent` self-purchase bypass

## Pinned source
- **Repo/commit:** SecondSwap @ `6693d9e4f03a37919a52626de64b1cadf632fd29`
- **`SecondSwap_Marketplace.sol` sha256 (first 14):** `80573b863544a3` (verified before and after patch testing).

## Affected contracts / functions
- `SecondSwap_Marketplace.sol` — `_validatePurchase` (private), reached via `spotPurchase`.
- `SecondSwap_VestingManager.sol` — `completePurchase`, `listVesting`.

## Exact source references
- `SecondSwap_Marketplace.sol:387-404` — `_validatePurchase`: checks listing status, `msg.sender != _referral`,
  whitelist, amount bounds; **no `buyer != seller` check**.
- `SecondSwap_VestingManager.sol:161-164` — `completePurchase`: `allocations[buyer][vesting].bought += amount`
  (unconditional), then `transferVesting(address(this), buyer, amount)`.
- `SecondSwap_VestingManager.sol:121-140` — `listVesting`: `sellLimit = bought + maxSellPercent *
  (currentAlloc + sold - bought) / BASE`; `require(sold <= sellLimit, "SS_VestingManager: cannot list more than
  max sell percent")`.

## Proof of Concept
- **PoC file:** `M11SelfPurchasePoC.t.sol` (placed under `test/audit/` of a local clone of the repo at the
  pinned commit; an archived copy travels with this package).
- **Harness:** self-contained Foundry fixture — deploys the real `SecondSwap_VestingManager`,
  `SecondSwap_Marketplace`, `SecondSwap_MarketplaceSetting`, `SecondSwap_StepVesting`, with `MockERC20` for the
  vesting token and the payment currency. No fork. No in-scope contract modified (except the temporary patch
  below, then restored).

### Vulnerable run
```
$ forge test --match-test test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent -vv

[PASS] test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent() (gas: 1428572)
Suite result: ok. 1 passed; 0 failed; 0 skipped
```
Assertions proven: baseline cap enforced (list above `A/5` reverts) → self-purchase succeeds → `bought` credited
→ `sellLimit` rises → after 5 cycles cumulative `sold == A` (full allocation, 5× the cap) → external buyer
receives real vested tokens and holder receives currency.

### Patch validation
Minimal patch added to `_validatePurchase`:
```solidity
require(msg.sender != listing.seller, "SS_Marketplace: no self purchase");
```
```
$ forge test --match-test test_M11_Patch_SelfPurchaseReverts -vv

[PASS] test_M11_Patch_SelfPurchaseReverts() (gas: 451556)
Suite result: ok. 1 passed; 0 failed; 0 skipped
```
Asserts: self-purchase reverts with `"SS_Marketplace: no self purchase"`, and a genuine third-party purchase
still succeeds.

## Source restoration / hash verification
After patch testing, `SecondSwap_Marketplace.sol` was restored to its original content and re-hashed:
`sha256 (first 14) = 80573b863544a3` — identical to the pinned source. No in-scope contract is left modified.

## Caveats
- **Local fixture:** the PoC deploys the in-scope contracts locally with mock tokens; it demonstrates the
  contract logic at the pinned commit, not a specific live deployment.
- **No external dependence:** the proof is derived solely from the cited in-scope source and the executable test;
  it does not depend on any external report, answer key, or third-party writeup.
