# P145 — Problem Statement

P143 ran a Level-3 runtime PoC for noya B1 (RUNTIME_CONFIRMED); P144 found B1 is the known/awarded noya H-03
(DUPLICATE_KNOWN_LOCALLY), so it can't advance as novel. **P145 pivots the same runtime-PoC method to a different
architecture (blackhole) and a different bug class (sibling-function recipient parity)** — to show the loop
generalizes and to runtime-confirm B5 (`RewardsDistributor.claim_many`).

## Prompt-derived mechanism (P138/P141, unchanged)
`claim` corrects the reward recipient for AVM-managed NFTs (`avm.getOriginalOwner`), but the batch sibling
`claim_many` omits that correction and pays `ownerOf` — so an AVM-managed tokenId's reward is misdirected to the
AVM manager instead of the original owner.

## Primary question
Does the real `RewardsDistributor.claim_many` send an AVM-managed tokenId's reward to the wrong recipient
(`ownerOf` / AVM manager) versus the sibling `claim` (`getOriginalOwner` / original owner), at runtime?

## Answer
**Yes — RUNTIME_CONFIRMED.** The real contract, deployed locally with mock VE/AVM/token, paid the original owner
on `claim(idA)` (1e18 → 0xBEEF) but the AVM manager on `claim_many([idB])` (1e18 → 0xA814) for equivalent
AVM-managed tokenIds; a non-AVM control showed no divergence. The protocol's own `claim` is the corrected
reference.

## Discipline (carried from P143/P144)
`prompt_decision` / `runtime_status` / `submission_status` kept strictly separate; runtime_confirmed = mechanism
evidence only; **not submission-ready**. B5 is the known blackhole **M-04** (DUPLICATE_KNOWN), so this is method
validation across a second architecture, not a submission. Human review + scope/duplicate/severity remain
mandatory.
