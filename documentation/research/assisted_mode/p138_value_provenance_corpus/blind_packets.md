# P138 — Blind Packets (neutral; what each subagent received)

Each subagent received the deep_pass_value_provenance prompt + ONE bundle = function body + direct callees +
a NEUTRAL one-line intended-semantics. NO sibling functions, NO bug/role hints (the P137-T3 lesson), NO answer
key. Sources are verbatim from each audit's on-disk Solidity. Full inlined bundles are in the run transcript;
summarized here for the record.

- B1 NoyaValueOracle: getValue wrapper + 4-arg _getValue (candidate) + 3-arg _getValue callee + priceRoutes/
  priceSource mappings + neutral routing semantics ([s0,s1] = asset→s0→s1→base).
- B2 MorphoBlueConnector._getPositionTVL + convertCToL callee + factual Morpho share→asset primitive notes
  (toAssetsUp) + neutral "returns TVL in base". (No "borrow is a debt" hint.)
- B3 BalancerConnector._getPositionTVL + totalLpBalanceOf callee + factual weighted-pool weight scaling note +
  neutral "returns base value of the vault's LP holding".
- B4 SellCreditMarket.validateSellCreditMarket + neutral domain notes (amount=cash, credit=face value,
  minimumCreditBorrowAToken=min credit, credit≥cash) — facts, not the bug.
- B5 RewardsDistributor.claim_many + _claim callee note + factual AVM note (ownerOf returns AVM contract vs
  getOriginalOwner returns user for AVM-managed tokenIds). [This factual context is necessary + somewhat leading
  — flagged as "aided" in grading.]
- C1 RewardsDistributor.claim (same AVM note as B5, for parallel fairness).
- C2 MorphoBlueConnector.convertCToL. C3 RewardsDistributor.claimable. C4 ChainlinkOracleConnector.getTokenDecimals.
  C5 AccountingLibrary.debtTokenAmountToCollateralTokenAmount (+ factual amountToWad/mulDivUp/getPrice notes).
