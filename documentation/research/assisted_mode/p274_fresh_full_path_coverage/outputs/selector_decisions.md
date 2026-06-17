# Pairwise mechanism selector — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| case | M1 (impact) | M2 (impact) | gap | anti-easy-PoC | outcome | decisive |
|---|---|---|---|---|---|---|
| pair_0 | LiquidationDistributor.distribute mis-splits liquidation proceeds across tranches (seniority/excess pro-rata) (9) | Pool.redeem/withdraw share rounding dust (2) | 7 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| pair_1 | MultiSourceLoan._processOffersFromExecutionData accepts mismatched/under-validated offer terms (9) | MultiSourceLoan.mergeTranches griefing on tranche consolidation (3) | 6 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| pair_2 | AuctionWithBuyoutLoanLiquidator.settleWithBuyout main-lender buyout authorization/timing/hash binding (9) | Pool/WithdrawalQueue withdrawal-queue rotation can strand or block claims (liveness) (9) | 0 | no | **KEEP_BOTH** | near-equal impact, both plausible -> keep both |
