# P118 — Source trace: SecondSwap_Marketplace.unlistVesting (secondswap-2024-12)

Subject: `contracts/SecondSwap_Marketplace.sol`. Read-only; framing only — runtime decides.

## unlistVesting(address _vestingPlan, uint256 _listingId) external isFreeze
```
Listing storage listing = listings[_vestingPlan][_listingId];
require(listing.status == Status.LIST, "SS_Marketplace: Listing not active");          // status guard
require(listing.seller == msg.sender || msg.sender == s2Admin(), "SS_Marketplace: Not the seller"); // ACCESS guard
if (msg.sender != s2Admin()) {                                                          // early-unlist penalty
    if (listing.listTime + minListingDuration() > block.timestamp) {
        require(usdt().balanceOf(msg.sender) >= penaltyFee(), "SS_Marketplace: Penalty fee required for early unlisting");
        usdt().safeTransferFrom(msg.sender, feeCollector(), penaltyFee());
    }
}
IVestingManager(vestingManager()).unlistVesting(listing.seller, _vestingPlan, listing.balance); // return balance
listing.status = Status.DELIST;   // flip status
listing.balance = 0;              // zero balance -> cannot return twice
emit Delisted(...);
```
- **Access control**: only `listing.seller` or `s2Admin` may unlist. (Carries inline audit-fix annotations
  3.3/3.4/3.6/3.7 — previously audited + patched.)
- **Anti-double-unlist / anti-double-return**: requires `status == LIST`, then flips to `DELIST` and sets
  `balance = 0`; a second call reverts on the status guard. The vesting balance is returned to the seller exactly
  once.
- **Defaults (MarketplaceSetting)**: `s2Admin = constructor arg`, `penaltyFee = 10 ether`, `minListingDuration = 120`.

## Lifecycle context
`listVesting(...)` creates `listings[plan][nextListingId++]` with `status = LIST`, `seller = msg.sender`,
`balance = total = _amount`. `spotPurchase` decrements `balance` and reverts once a listing is not active.

## actor_clarity precision gap (why it ranked high)
The P106/P107 role-guard detector matches `only[a-z]+` / `require(msg.sender ==` / `_checkRole` / `hasRole`. Here the
access control is written `require(listing.seller == msg.sender || msg.sender == s2Admin())` — the dispositive guard
is `seller == msg.sender` (operand-reversed) and `msg.sender == s2Admin()` is not the literal `require(msg.sender==`
prefix. So `actor_clarity` marked `unlistVesting` PERMISSIONLESS, over-ranking it. **This is a second, distinct
actor_clarity gap** (P115 fixed signature modifiers; this is the body-level `X == msg.sender` form). It does not
change P118's verdict (runtime decides) but is a concrete future ranking-precision fix.

## Framed runtime question
Despite the "permissionless" flag, can a non-seller/non-admin actually unlist a seller's active listing, or can a
listing be unlisted (balance returned) twice? → answered by the harness, not this trace.
