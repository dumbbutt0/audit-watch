# Minimal reproduction hypothesis

Candidate: `phi-2024-08 :: PhiNFT1155.claimFromFactory`.

## Source-backed hypothesis attempt

Read PhiNFT1155.claimFromFactory. It is `external payable whenNotPaused onlyPhiFactory` — gated to the PhiFactory contract, NOT permissionless. (Same ranking gap: the body-only actor_clarity heuristic missed the `onlyPhiFactory` MODIFIER in the signature.) The attacker-facing entrypoint is `PhiFactory.claim`; the reward flow (handleRewardsAndGetValueSent) is cross-contract via PhiRewards. I could not form a source-provable exploit on claimFromFactory in isolation, nor prove it safe. Truthful terminal: NEEDS_CONTEXT.

## What runtime evidence would be required

A falsifiable runtime check could not be specified from source alone for this candidate (see rationale). Resolving it would require execution-backed evidence — e.g. a fork/local deployment plus a differential or invariant test across the cross-contract boundary named above — not further source reasoning. Absent that, the truthful terminal is `NEEDS_CONTEXT`; no exploit is claimed and no finding is promoted.
