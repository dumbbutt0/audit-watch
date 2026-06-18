# RustFund (CodeHawks 2025-03) — Awarded Findings (revealed at adjudication)

Source: https://codehawks.cyfrin.io/c/2025-03-rustfund (4 High / 3 Medium). Reconstructed at REVEAL from the
CodeHawks public submission/report pages (titles not on the results summary; gathered post-blind-pass). Titles
only — token-overlap adjudication, never matched against source.

## High Risk Findings
- H-01 | Users get no refunds — contribute() never updates contribution.amount
- H-02 | Creator can withdraw funds before the deadline / goal is reached (rug)
- H-03 | Reentrancy / Checks-Effects-Interactions violation — withdraw/refund transfer before updating state
- H-04 | Direct lamport manipulation via try_borrow_mut_lamports — non-atomic / unsafe SOL transfer

## Medium Risk Findings
- M-01 | Unchecked arithmetic overflow in fund.amount_raised += amount (use checked_add/checked_sub)
- M-02 | Wrong conditional check in the contribute function
- M-03 | Missing/weak validation on set_deadline (arbitrary deadline)
