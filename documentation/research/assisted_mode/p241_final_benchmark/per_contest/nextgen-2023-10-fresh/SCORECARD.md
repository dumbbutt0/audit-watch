# nextgen SCORECARD — awarded 5H+12M (read: AuctionDemo full; Minter/Core UNREAD)
- H-03 push-refund griefing = NEXT-01 **HIT**; H-05 unbounded-loop DoS = NEXT-03 **HIT**.
- M-05 wrong recipient / M-07 callback-blocks-payment / M-11 unchecked-return ≈ NEXT-01/02/04 **PARTIAL**.
- H-02 timestamp-equality drain = **MISS** (Reasoning Depth — read AuctionDemo, missed ==endTime overlap).
- H-01 mint reentrancy, H-04 phases, M-01..M-04/M-06/M-08/M-09/M-12 = **MISS** (Coverage: MinterContract/NextGenCore/Randomizers UNREAD).
- NEXT-02 (returnHighestBidder no-highBid-update) base candidate: real bug but maps at best to M-05 partial / likely QA → mild over-rate.
- Recall: High 2 clean /5; Medium ~partials. Lens 0.
