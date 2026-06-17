# Minimal reproduction hypothesis

Candidate: `munchables-2024-07 :: MigrationManager.burnNFTs`.

## Source-backed hypothesis attempt

Read MigrationManager.burnNFTs. `external override`, `seal`-gated, caller guard (`_user == msg.sender` OR target user chose an action); bounded paginated loop burning the user's LOCKED, unclaimed NFTs and awarding points. Same class as burnRemainingPurchasedNFTs — a force-burn/wrong-choice griefing path is conceivable but needs the full migration lifecycle + runtime to confirm/refute. No source-provable exploit; not provably safe. Truthful terminal: NEEDS_CONTEXT.

## What runtime evidence would be required

A falsifiable runtime check could not be specified from source alone for this candidate (see rationale). Resolving it would require execution-backed evidence — e.g. a fork/local deployment plus a differential or invariant test across the cross-contract boundary named above — not further source reasoning. Absent that, the truthful terminal is `NEEDS_CONTEXT`; no exploit is claimed and no finding is promoted.
