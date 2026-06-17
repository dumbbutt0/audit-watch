# P230 measurement artifact — TraitForge (NFT/Gaming) blind candidate set

Subject: `audits/traitforge-2024-07-fresh` (ERC-721 breeding/forging game + nuke honeypot). Keys SEALED (no sealed key existed; the public 4naly3er static report was avoided for purity).
Method: blind Sonnet deep_trace pass driven by `prompts/deep_trace.md` + `agents/{token_integration,access_control,logic,economic_attack,arithmetic,reentrancy,dos}.md` + `config/{token_standard_patterns,griefing_dos_patterns}.json`.
Full raw output: session tool-result `toolu_01ET3bsVUgG4t35EKm8mMi94.json`. Tally: 26 candidates — HIGH 6 · MED 12 · LOW 6 · NOISE 2.

| id | title | bug class | contract | conf | signal |
|---|---|---|---|---|---|
| TF-01 | golden-slot (999999) entropy predictable/manipulable by searcher | oracle/invariant | EntropyGenerator | High | HIGH |
| TF-02 | writeEntropyBatch1/2/3 permissionless → anyone seeds entropy table | access-control/invariant | EntropyGenerator | Confirmed | HIGH |
| TF-03 | _cancelListingForForging leaves stale listedTokenIds mapping | state-transition/accounting | EntityForging | Medium | MED |
| TF-04 | forgeWithListed pays forgerOwner post-mint → griefing via revert | reentrancy/routing | EntityForging | Medium | MED |
| TF-05 | NukeFund fund tracker diverges from balance (force-send / revert paths) | accounting/invariant | NukeFund | High | HIGH |
| TF-06 | nuke() burn→airdrop external call reentrancy before ETH send | reentrancy | NukeFund | Medium | MED |
| TF-07 | buyNFT pays seller before NFT transfer (CEI) → reenter | reentrancy/state-transition | EntityTrading | High | MED |
| TF-08 | nuke holding-period uses lastTokenTransferredTimestamp=0 on mint → age huge | logic/invariant | NukeFund | Medium | MED |
| TF-09 | mint price uses per-generation count → resets near startPrice each gen | economic/accounting | TraitForgeNft | Speculative | LOW |
| TF-10 | getNextEntropy `<= maxSlotIndex` off-by-one OOB slot 770 | arithmetic/invariant | EntropyGenerator | High | MED |
| TF-11 | forgeWithListed increments forgingCounts before potential check | state-transition/accounting | EntityForging | Speculative | LOW |
| TF-12 | DevFund receive integer-division dust; remaining to owner not fund | arithmetic/accounting | DevFund | High | MED |
| TF-13 | buyNFT listings[0] zero-struct guard (correctly blocks) | logic | EntityTrading | Medium | LOW |
| TF-14 | _beforeTokenTransfer calls forging cancel unconditionally → transfers revert if unset/paused | access-control/dos | TraitForgeNft | High | HIGH |
| TF-15 | mintWithBudget refund .call to msg.sender → reverting fallback DoSes minter | dos/reentrancy | TraitForgeNft | High | MED |
| TF-16 | NukeFund devShare routing/event inconsistency | accounting/routing | NukeFund | High | MED |
| TF-17 | initializeAlphaIndices onlyOwner but called by non-owner TraitForgeNft → generation increment always reverts (bricks minting) | access-control/state-transition | EntropyGenerator/TraitForgeNft | Confirmed | HIGH |
| TF-18 | entropy batch index bounds (analyzed correct) | arithmetic | EntropyGenerator | Speculative | LOW |
| TF-19 | forge entropy = (a+b)/2 → forger can target specific entropy | economic/oracle | TraitForgeNft | Medium | MED |
| TF-20 | nuke factor: ageMultiplier=0 default → only initialNukeFactor applies | logic/accounting | NukeFund | High | MED |
| TF-21 | forgeWithListed listing not cancelled before payouts → reenter re-list | reentrancy/state-transition | EntityForging | Speculative | LOW |
| TF-22 | _beforeTokenTransfer paused() checked after external cancel call | logic/state-transition | TraitForgeNft | Medium | MED |
| TF-23 | merkle leaf = keccak(msg.sender) only → whitelist replay cross-chain/redeploy | access-control | TraitForgeNft | Medium | MED |
| TF-24 | getNextEntropy wraps to slot 0 after 10,010 values → entropy cycles/repeats | invariant/oracle | EntropyGenerator | High | HIGH |
| TF-25 | nuke fund -= before burn (analyzed CEI-ok) | state-transition/accounting | NukeFund | Speculative | NOISE |
| TF-26 | fetchListings allocates over monotonic listingCount → unbounded growth DoS | dos/accounting | EntityForging | High | MED |
