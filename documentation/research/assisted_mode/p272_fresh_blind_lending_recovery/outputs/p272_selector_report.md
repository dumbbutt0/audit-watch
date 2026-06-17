# Pairwise mechanism selector — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| case | M1 (impact) | M2 (impact) | gap | anti-easy-PoC | outcome | decisive |
|---|---|---|---|---|---|---|
| L1_liq_incentive | LiqIncentiveCalculator.getLiqIncentiveMultiplier_e18 applies min-floor AFTER max-cap (Math.max(min(...,max),min[mode])); misconfigured/edge min>max -> over-incentive multiplier -> liquidator over-seizes collateral (6) | liquidate reverts on edge health input (3) | 3 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| L2_health_zero_baddebt | InitCore.liquidate: health_e18==0 (underwater) -> getLiqIncentiveMultiplier returns 0 -> repayAmtWithLiqIncentive=0 -> no collateral seized + post-liq health check bypassed -> underwater positions cannot be liquidated / bad debt unrecoverable (6) | health==0 emits a misleading event (3) | 3 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| L3_collateral_credit | InitCore.getCollateralCreditCurrent_e36 collateral-credit/health miscalc enabling over-borrow or under-liquidation (12) | collateral-credit rounding dust (1) | 11 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| Lneg_harvest | PosManager.harvest reward manipulation (claimed systemic) but unsupported (12) | harvest benign (3) | 9 | no | **REFUTE_M1_FIRST** | terminal_impact(high) but refuted -> refute before trusting |
