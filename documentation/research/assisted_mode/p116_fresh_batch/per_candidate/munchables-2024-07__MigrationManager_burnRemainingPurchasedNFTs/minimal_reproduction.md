# Minimal reproduction hypothesis

Candidate: `munchables-2024-07 :: MigrationManager.burnRemainingPurchasedNFTs`.

## Source-backed hypothesis attempt

Read MigrationManager.burnRemainingPurchasedNFTs. `external override`, gated by a `seal` flag and a caller guard (`_user == msg.sender` OR the target user has already chosen a migration action). It sets `_userPurchasedAction[_user]=LOCKED_BURN` then burns the user's UNLOCKED, unclaimed purchased NFTs in a bounded paginated loop (_skip..SKIP_AMOUNT). A possible griefing path — calling for another `_user` who has set an action, forcing a burn/choice — depends on the full migration state machine (`_userPurchasedAction` semantics) and would need runtime to confirm or refute. No source-provable exploit; not provably safe. Truthful terminal: NEEDS_CONTEXT.

## What runtime evidence would be required

A falsifiable runtime check could not be specified from source alone for this candidate (see rationale). Resolving it would require execution-backed evidence — e.g. a fork/local deployment plus a differential or invariant test across the cross-contract boundary named above — not further source reasoning. Absent that, the truthful terminal is `NEEDS_CONTEXT`; no exploit is claimed and no finding is promoted.
