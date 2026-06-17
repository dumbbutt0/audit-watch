# P121 — Minimal runtime question

> **Can a permissionless caller of `nuke(tokenId)` extract more than the designed cap (≤50% of fund per call),
> claim without satisfying the ownership/approval/maturity guards, re-nuke a burned token, or drive the fund
> accounting to underflow / insolvency?**

One question. The harness answers it; source only frames it.

## YES (CONFIRMED) would require
An executed test in which a caller claims > fund/2 in one call, nukes a token it doesn't own / isn't approved for /
isn't mature, nukes the same token twice, or makes `fund` underflow or the contract ETH balance fall below `fund`.

## NO (KILLED) requires
Executed tests showing the three guards revert unauthorized/unapproved/immature calls, the claim equals exactly the
capped/proportional amount (≤ fund/2), a burned token cannot be re-nuked, and `fund` stays ≥ 0 with the contract
solvent across multiple nukes.

## Scope
- Primary = over-claim / guard-bypass / re-nuke / insolvency by a permissionless caller (the high-value reading of a
  permissionless fund-claiming function).
- **Out of scope (NEEDS_CONTEXT):** cross-contract maturity bypass (`getTokenLastTransferredTimestamp == 0` at mint)
  and entropy bounds — these depend on the real `TraitForgeNft` mint/entropy machinery, not settleable by a mock NFT.
- `ageMultiplier` and other params are owner-set; owner mis-configuration is out of the permissionless-attacker scope.
