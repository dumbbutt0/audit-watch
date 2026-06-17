# Pairwise mechanism selector — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| case | M1 (impact) | M2 (impact) | gap | anti-easy-PoC | outcome | decisive |
|---|---|---|---|---|---|---|
| L1_pendle_share | PendlePowerFarmToken share-price/first-deposit/rounding manipulation (_getSharePrice=assets/totalSupply, mintFee+sync) (12) | mintFee rounding dust (1) | 11 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| L2_liquidation | WiseCore _withdrawPureCollateralLiquidation/_withdrawOrAllocateSharesLiquidation share/collateral misallocation (6) | liquidation path UX revert on edge input (3) | 3 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| L3_baddebt | FeeManager paybackBadDebtForToken/NoReward bad-debt accounting error (6) | bad-debt event emission / minor rounding (3) | 3 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| Lneg_posnft | PositionNFTs mint manipulation (claimed systemic) but unsupported (12) | PositionNFTs mint benign (3) | 9 | no | **REFUTE_M1_FIRST** | terminal_impact(high) but refuted -> refute before trusting |
