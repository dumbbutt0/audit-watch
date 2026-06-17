# `maxSellPercent` sell-cap can be bypassed by purchasing your own listing

**Severity:** Medium
**Target:** SecondSwap (commit `6693d9e4f03a37919a52626de64b1cadf632fd29`)
**Affected contracts:** `SecondSwap_Marketplace.sol`, `SecondSwap_VestingManager.sol`

## Summary
The marketplace is intended to limit how much of a vesting holder's **locked** allocation can be sold on the
secondary market, via a per-holder `maxSellPercent` cap enforced in `SecondSwap_VestingManager.listVesting`.
Because `SecondSwap_Marketplace._validatePurchase` does not prevent a buyer from being the same address as the
seller, a holder can buy their **own** listing. Each self-purchase credits the holder's `bought` counter, which
feeds back into the sell-limit formula at full value. By repeating list → self-purchase cycles, a holder
inflates their `bought` counter and raises their effective sell limit without bound, ultimately selling their
**entire** locked allocation despite `maxSellPercent`. The only cost is marketplace fees.

## Vulnerability details
`SecondSwap_VestingManager.listVesting` computes the allowed sell amount as:

```solidity
uint256 sellLimit = userAllocation.bought;
uint256 currentAlloc = SecondSwap_Vesting(plan).total(seller);
if (currentAlloc + userAllocation.sold > userAllocation.bought) {
    sellLimit += ((currentAlloc + userAllocation.sold - userAllocation.bought)
                  * vestingSettings[plan].maxSellPercent) / BASE;
}
userAllocation.sold += amount;
require(userAllocation.sold <= sellLimit, "SS_VestingManager: cannot list more than max sell percent");
```

So `sellLimit = bought + maxSellPercent * (currentAlloc + sold - bought) / BASE`. The `bought` term is added at
**100%**, while the capped term is taken over `(currentAlloc + sold - bought)`, which stays equal to the holder's
original allocation `A` across list/buy cycles. Therefore any increase in `bought` raises `sellLimit` one-for-one.

`bought` is increased by `SecondSwap_VestingManager.completePurchase`, which is called by the marketplace on every
purchase and credits the buyer unconditionally:

```solidity
function completePurchase(address buyer, address vesting, uint256 amount) external onlyMarketplace {
    allocations[buyer][vesting].bought += amount;
    SecondSwap_Vesting(vesting).transferVesting(address(this), buyer, amount);
}
```

The purchase validation in `SecondSwap_Marketplace._validatePurchase` never checks that the buyer differs from the
seller:

```solidity
require(listing.status == Status.LIST, "SS_Marketplace: Listing not active");
require(msg.sender != _referral, "SS_Marketplace: Invalid referral");
require(listing.whitelist == address(0) || IWhitelist(listing.whitelist).validateAddress(msg.sender), "...");
// ... amount checks ...
// (no buyer != seller check)
```

So a holder can purchase their own public listing, which increments their own `bought`, which raises their own
future `sellLimit`.

## Root cause
Two reinforcing issues:
1. `_validatePurchase` permits self-purchase (no `buyer != seller` guard).
2. The sell-limit formula treats `bought` as fully sellable headroom and adds it at 100%, so a holder can mint
   sell-headroom for their locked allocation simply by routing tokens through purchases — including purchases
   from themselves.

## Attack scenario
Let a holder have an original locked allocation `A`, with `maxSellPercent = 20%` (intended cap `A/5`):
1. Holder lists `A/5` (the maximum currently permitted). A list of even `+1` more reverts with
   `"cannot list more than max sell percent"` — the cap is correctly enforced at this point.
2. Holder calls `spotPurchase` on their **own** listing. `completePurchase` credits `bought += A/5` and returns
   the tokens to the holder.
3. `sellLimit` is now `A/5 + maxSellPercent * A / BASE = 2 * (A/5)`. The holder can list another `A/5`.
4. Repeating the list → self-purchase cycle five times drives cumulative `sold` to `A` — the **full** locked
   allocation, i.e. 5× the intended 20% cap — with every listing passing the `require(sold <= sellLimit)` check.
5. Any of those tranches (e.g. the final one) can be sold to a genuine third-party buyer, who receives real
   vested tokens while the holder receives payment. The holder's net cost across the cycles is only the
   marketplace fees.

## Impact
The `maxSellPercent` restriction — a core control on how much of a locked vesting allocation can reach the
secondary market — is bypassable by any holder for the price of marketplace fees. A holder can liquidate their
entire locked allocation regardless of the configured cap. This is a violation of an intended protocol
restriction with real economic consequence (uncontrolled secondary-market dumping of locked allocations), but it
does not, by itself, steal third-party funds — hence Medium.

## Proof of Concept
A self-contained Foundry test exercises the real in-scope contracts (`SecondSwap_VestingManager`,
`SecondSwap_Marketplace`, `SecondSwap_StepVesting`) with mock ERC20 tokens.

**Test file:** `M11SelfPurchasePoC.t.sol`

**Test command:**
```
forge test --match-test test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent -vv
```

**Actual result (vulnerable source):** PASS. The test asserts, in order: (1) the cap is enforced before the
exploit (a list above `A/5` reverts); (2) the holder can buy their own listing; (3) `bought` increases from the
self-purchase; (4) `sellLimit` rises so the holder can list beyond the cap; (5) after five cycles cumulative
`sold` reaches the full allocation `A`; (6) a separate external buyer receives real vested tokens and the holder
receives currency.

**Expected result (correct behaviour):** A holder should never be able to make `sold` exceed
`maxSellPercent * A / BASE` for their original locked allocation. Step (1) should remain true after any sequence
of purchases the holder makes; self-purchase should not increase sellable headroom.

## Recommended mitigation
- Reject self-purchase in `_validatePurchase`:
  ```solidity
  require(msg.sender != listing.seller, "SS_Marketplace: no self purchase");
  ```
- Additionally, reconsider crediting `bought` at 100% into `sellLimit`: marketplace-internal transfers (and any
  acquisition that should not relax the cap on a holder's *original* locked allocation) should not increase a
  holder's sellable headroom. Track and cap sellability against the original allocation rather than a counter a
  holder can inflate.

A one-line `buyer != seller` guard was verified to stop the demonstrated exploit (self-purchase reverts) while
leaving genuine third-party purchases working; see the evidence bundle. A complete fix should address the
`bought`-inflation aspect as well, since cooperating addresses could approximate the same effect at higher fee
cost.

## Assumptions / limitations
- The cap is `sellable`-enabled and configured (`maxSellPercent > 0`); the PoC uses the contract default of 20%.
- The attack costs marketplace fees per cycle; it is economically rational when the value of liquidating the
  locked allocation exceeds those fees.
- The PoC is a local deployment of the in-scope contracts with mock tokens (no fork); it demonstrates the
  contract logic, not a specific live deployment's parameters.
