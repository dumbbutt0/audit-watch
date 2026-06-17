# P270 — IMPACT_FIRST_TRIAGE (Phase 4)

Frozen **P269** impact-first triage (`impact_first_poc_triage.py`, `63c88d02d2c7eefa`) over the advisory candidates +
selector outputs. Input `outputs/p270_triage_input.json` (`101c85ba1ed1ca61`); decisions
`outputs/p270_triage_decisions.json` (`d00487303f8cb2b5`); guard PASS, 0 violations. **selected_count = 3.**

| candidate | subsystem | impact_class | fit | heavy | outcome |
|---|---|---|---|---|---|
| **pp_share_inflation** | pendle_power_farm | insolvency | 16 | **Y** | **SELECT_FOR_PARTIAL_RUNTIME** |
| **fm_baddebt_acct** | feemanager_baddebt | bad_debt | 16 | **Y** | **SELECT_FOR_PARTIAL_RUNTIME** |
| **wc_liq_misalloc** | wisecore_liquidation | liq_redemption_blockage | 15 | **Y** | **SELECT_FOR_PARTIAL_RUNTIME** |
| nft_mint_drama | position_nfts | insolvency (unsupported) | 14 | - | DEFER_LOW_IMPACT |
| wc_liq_revert | wisecore_liquidation | griefing_minor | 5 | - | KEEP_AS_CONTROL |
| pp_mintfee_dust | pendle_power_farm | dust_rounding | 3 | - | KEEP_AS_CONTROL |

## The P270-critical result (the P268 fix, live on fresh data)
All three high-impact award-class subsystems need a **heavy** harness (full wise-lending stack / Pendle fork /
snapshot scaffolding — `feasibility_blockers` = needs_fork / needs_snapshot_scaffolding). P269 routes them
**SELECT_FOR_PARTIAL_RUNTIME (heavy_poc=true)** — i.e. *routed into the PoC path*, **not de-scoped**. This is exactly
the inverse of the P268 failure (where the heavy award subsystem was dropped for the easy one). The unsupported NFT
drama is deferred (anti-drama); the easy low-impact rivals are controls, not selections.

## Selection rules satisfied
- 3 candidates selected (within the 3–5 band).
- ≥1 recall-delta: all three are recall-delta.
- ≥1 high-impact award-class-fit: all three (insolvency/bad-debt/liquidation).
- subsystem clusters: pendle_power_farm, feemanager_baddebt, wisecore_liquidation each get a routed representative.
- heavy candidates NOT de-scoped for fixture difficulty → PARTIAL_RUNTIME.
- controls kept only as KEEP_AS_CONTROL (do not displace high-impact).

## Expected mechanism + falsifier (per selected) — carried to completion/PoC
- pp_share_inflation: share-price = assets/totalSupply, first-deposit/rounding manipulation; falsifier =
  `_validateSharePriceGrowth` time-bound caps early inflation.
- fm_baddebt_acct: bad-debt payback bookkeeping error across paybackBadDebtForToken/NoReward; falsifier = bookkeeping
  reconciles across paths.
- wc_liq_misalloc: liquidation collateral/share misallocation; falsifier = security checks bound the allocation.
Frozen before completion.
