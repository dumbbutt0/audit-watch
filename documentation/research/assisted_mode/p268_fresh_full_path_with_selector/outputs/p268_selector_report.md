# Pairwise mechanism selector — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| case | M1 (impact) | M2 (impact) | gap | anti-easy-PoC | outcome | decisive |
|---|---|---|---|---|---|---|
| C1_redeem | permissionless finishRedeem + spot/donation accounting manipulation (10) | startRedeem self-approval requirement -> griefing revert (3) | 7 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| C2_mint_inflation | first-depositor share-inflation via donation (9) | tiny-deposit zero-share rounding (1) | 8 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| Cneg_slashing | slashing manipulates vault accounting (10) | gated, no permissionless path (3) | 7 | no | **REFUTE_M1_FIRST** | terminal_impact(high) but refuted -> refute before trusting |
