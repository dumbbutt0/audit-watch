# Impact-first PoC triage — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| id | subsystem | impact_class | fit | recall-Δ | feasibility | heavy | outcome |
|---|---|---|---|---|---|---|---|
| pp_share_inflation | pendle_power_farm | insolvency | 16 | Y | hard | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| fm_baddebt_acct | feemanager_baddebt | bad_debt | 16 | Y | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| wc_liq_misalloc | wisecore_liquidation | liq_redemption_blockage | 15 | Y | heavy | Y | **SELECT_FOR_PARTIAL_RUNTIME** |
| nft_mint_drama | position_nfts | insolvency | 14 | Y | easy | - | **DEFER_LOW_IMPACT** |
| wc_liq_revert | wisecore_liquidation | griefing_minor | 5 | - | easy | - | **KEEP_AS_CONTROL** |
| pp_mintfee_dust | pendle_power_farm | dust_rounding | 3 | - | easy | - | **KEEP_AS_CONTROL** |
