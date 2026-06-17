# P121 — Source trace: NukeFund.nuke (traitforge-2024-07)

Subject: `contracts/NukeFund/NukeFund.sol`. Read-only; cited for framing only — runtime decides.

## nuke (the claim path)
`function nuke(uint256 tokenId) public whenNotPaused nonReentrant` — resource-scoped permissionless.
1. `require(nftContract.isApprovedOrOwner(msg.sender, tokenId))` — caller must own/be approved for the token.
2. `require(getApproved(tokenId) == address(this) || isApprovedForAll(msg.sender, address(this)))` — NukeFund must
   be approved to move the NFT.
3. `require(canTokenBeNuked(tokenId), 'Token is not mature yet')`.
4. `finalNukeFactor = calculateNukeFactor(tokenId)`.
5. `potentialClaimAmount = fund * finalNukeFactor / MAX_DENOMINATOR (100000)`.
6. `maxAllowedClaimAmount = fund / maxAllowedClaimDivisor (=2)`  → **50% of the current fund**.
7. `claimAmount = finalNukeFactor > nukeFactorMaxParam (50000) ? maxAllowedClaimAmount : potentialClaimAmount;`
   - branch A (factor > 50000): claim = fund/2.
   - branch B (factor ≤ 50000): claim = fund*factor/100000 ≤ fund*50000/100000 = fund/2.
   - **⇒ claim ≤ fund/2 in both branches** → `fund -= claimAmount` cannot underflow.
8. `fund -= claimAmount; nftContract.burn(tokenId); (success,) = payable(msg.sender).call{value: claimAmount}('');`
   - state updated (fund, burn) before the ETH send; `nonReentrant` guards the external `burn`/`call`.

## canTokenBeNuked / calculateNukeFactor / calculateAge
- `canTokenBeNuked`: `block.timestamp - getTokenLastTransferredTimestamp(tokenId) >= minimumDaysHeld (3 days)`.
- `calculateNukeFactor`: `entropy/40 + (calculateAge * defaultNukeFactorIncrease(250) / MAX_DENOMINATOR)`.
- `calculateAge`: `daysOld * (entropy % 10) * MAX_DENOMINATOR * ageMultiplier / 365` — `ageMultiplier` is owner-set.

## Funding (how `fund` gets value)
`receive()` adds `msg.value - msg.value/taxCut(10)` (90%) to the private `fund`; the 10% devShare is routed to
dev/owner/dao depending on airdrop state. So contract ETH balance tracks `fund` (≈ solvent by construction).

## Access surface
Setters (`setTaxCut`, `setMinimumDaysHeld`, `setNukeFactorMaxParam`, `setMaxAllowedClaimDivisor`, `setAgeMultplier`,
`setTraitForgeNftContract`, …) are all `onlyOwner` — out of the permissionless-attacker scope.

## Cross-contract scope limit (honest)
The strongest nuke questions are CROSS-CONTRACT and depend on the real `TraitForgeNft`:
- maturity bypass — does mint leave `getTokenLastTransferredTimestamp == 0` (→ `block.timestamp - 0` always mature)?
- entropy bounds feeding `calculateNukeFactor`.
These need the real TraitForgeNft mint/entropy machinery (EntropyGenerator + pricing + merkle) — out of a mock-NFT
harness. Recorded as NEEDS_CONTEXT. The harness decisively answers nuke's **internal claim/guard/accounting integrity**.

## Framed runtime question (→ harness)
Can a permissionless caller of `nuke(tokenId)` extract more than the ≤50%/call cap, bypass the ownership/approval/
maturity guards, re-nuke a burned token, or drive the fund to underflow/insolvency? → answered by the harness.
