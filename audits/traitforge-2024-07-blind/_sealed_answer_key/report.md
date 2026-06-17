# TraitForge (Code4rena 2024-07) — Awarded Findings (revealed at adjudication)

Source: code4rena.com/reports/2024-07-traitforge — 6 High / 19 Medium.

## High Risk Findings
- H-01 | Wrong minting logic based on total token count across generations — `mintWithBudget` checks `_tokenIds` (all-time) instead of `generationMintCounts[currentGeneration]`.
- H-02 | Griefing attack on seller's airdrop benefits — initial NFT owners lose airdrop entropy when subsequent owners burn/nuke transferred tokens (burn/nuke use `initialOwners`).
- H-03 | Incorrect percentage calculation in NukeFund and EntityForging when `taxCut` changed from default — uses `msg.value / taxCut` instead of a proper percentage; breaks when taxCut != 10.
- H-04 | Number of entities in generation can surpass 10k — `_incrementGeneration` resets `generationMintCounts` to 0 without accounting for already-forged entities in the new generation.
- H-05 | The maximum number of generations is infinite — no real max-generation enforcement despite the intended cap of 10.
- H-06 | `mintToken()`/`mintWithBudget()`/`forge()` fail due to wrong modifier in `EntropyGenerator.initializeAlphaIndices()` — uses `onlyOwner` instead of `onlyAllowedCaller`, so the NFT contract cannot call it on generation increment.

## Medium Risk Findings
- M-01 | Uninitialized `entropySlots` read in `getNextEntropy` -> 0 entropy mint.
- M-02 | Funds can be locked indefinitely in NukeFund (no withdrawal beyond nuke()).
- M-03 | A dev loses rewards if, after claiming, he mints an NFT.
- M-04 | Lack of slippage protection in dynamic pricing mint (`mintWithBudget`).
- M-05 | Incorrect check against golden entropy value in the first two batches.
- M-06 | Generations without a golden god are possible.
- M-07 | Discrepancy between nfts minted, price when generation changes, and position of `_incrementGeneration()`.
- M-08 | Lack of ability to make some external calls makes the DAO stage unreachable.
- M-09 | `Golden God` tokens can be minted twice per generation.
- M-10 | Imprecise token age calculation -> incorrect nuke factor.
- M-11 | Duplicate NFT generation via repeated forging with the same parent.
- M-12 | NFTs mature too slowly under default settings.
- M-13 | Pause and unpause functions are inaccessible.
- M-14 | Forger Entities can forge more times than intended.
- M-15 | Nuke DoSed for three days after listing and canceling sale.
- M-16 | No slippage check in `nuke()`.
- M-17 | Incorrect `isApprovedForAll` check in `NukeFund.nuke()`.
- M-18 | Excess ETH from `forgingFee` can get stuck in `EntityForging`.
- M-19 | Each generation should have 1 "Golden God" NFT, but there could be 0.
