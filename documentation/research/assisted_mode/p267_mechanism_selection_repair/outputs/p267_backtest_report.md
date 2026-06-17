# Pairwise mechanism selector — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| case | M1 (impact) | M2 (impact) | gap | anti-easy-PoC | outcome | decisive |
|---|---|---|---|---|---|---|
| A_P266_phi_H03 | distribute royalty+dust to arbitrary caller (one-off skim) (2) | curator-enumeration gas-DoS freezes reward distribution (12) | 10 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| B_P256_plaza_PL2_fee | repeated fee pricing over un-reset period (systematic worse pricing) (9) | redeem-before-claimFees reconciliation gap -> pool insolvency (12) | 3 | no | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC |
| C_P256_plaza_PL1_curve | create/redeem collateral-level basis asymmetry (6) | non-linear curve <=1.2 split-deposit convexity (mint more than deserved) (9) | 3 | no | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC |
| D_P257_notional_NL2_fee_accrue | exp-decay Taylor-approximation error (tidy, dust) (3) | accrue-timing fee dodge / NAV inconsistency (mint at stale-fee price) (9) | 6 | no | **SELECT_M2** | terminal_impact_dominance; rival weak/refuted |
| E_P255_bakerfi_L5_harvest | P&L-only-when-deltaDebt==0 (perf fee un-minted on adjustment harvest) (8) | harmless: adjustment harvest nets to no P&L (1) | 7 | YES | **SELECT_M1** | terminal_impact_dominance; rival weak/refuted; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| NC1_drama_but_refuted | dramatic insolvency claim but decisively refuted + privileged-only (12) | clean stranded-funds bug, permissionless, survives falsification (10) | 2 | no | **REFUTE_M1_FIRST** | terminal_impact(high) but refuted -> refute before trusting |
| NC2_two_weak_no_dominance | minor local misprice, easy to PoC (3) | higher-drama griefing, not clearly stronger (3) | 0 | no | **KEEP_BOTH** | near-equal impact, both plausible -> keep both |
