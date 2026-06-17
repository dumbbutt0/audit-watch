# P287 — POC_INTENT_FREEZE (pre-reveal; frozen BEFORE any PoC code)

One READY candidate. Frozen hypothesis = the pipeline's pre-reveal claim; the PoC tests it. Findings remain SEALED.

## Candidate: LRTDepositPool.getRsETHAmountToMint (SHARE_ROUNDING_PRECISION / oracle-normalization)
- **candidate_id**: coverage_manifest:LRTDepositPool:getRsETHAmountToMint:6
- **contract/function**: LRTDepositPool.getRsETHAmountToMint(address asset, uint256 amount) → rsethAmountToMint
- **mechanism hypothesis (pipeline, P284 D4.6)**: the rsETH mint amount is valued from an oracle price consumed without
  a staleness check or decimals normalization; a stale/unnormalized price mis-values the mint.
- **source basis**: `rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.getRSETHPrice()`;
  `ChainlinkPriceOracle.getAssetPrice` = `AggregatorInterface(feed).latestAnswer()` — no `updatedAt`/`roundId` staleness
  guard, no decimals normalization.
- **attacker path**: a depositor mints rsETH while the Chainlink feed answer is stale (feed not updated / paused); the
  pool consumes `latestAnswer()` regardless and computes the mint amount from a stale price.
- **impact delta**: minted rsETH amount diverges from the true asset/rsETH exchange rate → over- or under-mint of shares
  (value conservation broken; minter nets positive or protocol/other holders are diluted).
- **victim/gainer**: gainer = depositor minting at a favorable stale price; victim = protocol solvency / existing rsETH
  holders.
- **invariant**: the share↔asset conversion must use a fresh, correctly-scaled price; a stale `latestAnswer()` must not
  be silently consumed.
- **assertion (PoC)**: with a stale feed answer, `getRsETHAmountToMint` still returns a value computed from the stale
  price (no revert), and that value differs from the fresh-price reference → mis-mint. Control: an oracle WITH a
  staleness guard reverts on the stale read.
- **setup**: MockChainlinkAggregator (latestAnswer + updatedAt), ChainlinkPriceOracleRepro (latestAnswer, no staleness),
  a guarded variant (reverts if stale), and the mint formula.
- **tx sequence**: 1) feed set to a fresh price → record mint(amount); 2) feed goes stale (updatedAt old) with a drifted
  answer → mint(amount) still computed from the stale answer (no revert) → different rsETH amount.
- **control/refutation**: if the real getAssetPrice DID check staleness/normalize, the stale read would revert →
  PASS_REFUTED. (Source shows it does NOT, so PASS_SUPPORTED expected — but reported honestly either way.)
- **recommended tier**: C (faithful reproduction of the latestAnswer-without-staleness consumption path).

## Honest note
This is the pipeline's hypothesis, frozen pre-reveal. It is SOURCE-FAITHFUL (latestAnswer has no staleness guard) but
whether it matches an AWARDED kelp H/M is unknown until reveal; the locus flagged is the consumer (getRsETHAmountToMint),
the flaw lives in the transitively-called ChainlinkPriceOracle.getAssetPrice (same-area, correct mechanism).
