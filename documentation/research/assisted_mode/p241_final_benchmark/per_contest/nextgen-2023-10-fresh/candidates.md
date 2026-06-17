# P241 — NextGen (C4 2023-10) blind base candidates (pre-reveal)

Architecture: generative-art NFT (MinterContract + NextGenCore + AuctionDemo + Randomizers). **Read bound:**
AuctionDemo (full) + interfaces; MinterContract/NextGenCore (large, 33KB/25KB) NOT fully read — base recall here is
a LOWER BOUND. Answer key NOT opened.

| ID | Title | Contract:fn | Sev | Conf |
|---|---|---|---|---|
| NEXT-02 | `returnHighestBidder` never updates `highBid` in its loop (`if (bid > highBid && status) index=i;` with highBid fixed at 0) → returns the LAST active bidder, not the highest → wrong winner can claim (WinnerOrAdminRequired) and claim/refund logic mismatches the true highest bid | AuctionDemo:returnHighestBidder (87) | **High** | High |
| NEXT-01 | `claimAuction` loops all bids refunding losers via low-level `.call` with success IGNORED → a loser whose refund reverts permanently loses their bid funds (auctionClaim flag prevents retry) | AuctionDemo:claimAuction (104) | Medium | High |
| NEXT-03 | Auction bid accounting via unbounded array + per-claim O(n) refund loop → gas-griefing / block-gas-limit DoS on claim for popular auctions | AuctionDemo:claimAuction/cancelAllBids | Medium | Med |
| NEXT-04 | `claimAuction` sends highestBid to `owner()` but uses `returnHighestBidder` (buggy) to gate the NFT transfer → NFT-vs-funds mismatch (NFT may not transfer while funds move) | AuctionDemo:claimAuction (110-119) | Med/High | Med |
| NEXT-05 | (unread surface) MinterContract phases/allowlist + Randomizer predictability (RandomizerNXT/XRandoms) — flagged as likely areas but not fully read | MinterContract/Randomizers | ? | Speculative |

Advisory lenses on nextgen: Safe 0, hostile 0 (no Safe guard; NFT transfers + ETH refunds, no order-selected ERC20 settlement → out of lens domains). Lens contribution expected 0.
Harness: BLOCKED_BY_BUILD. Proof attempts 0.
