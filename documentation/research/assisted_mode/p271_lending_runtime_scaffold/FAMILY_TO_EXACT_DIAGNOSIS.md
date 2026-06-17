# P271 — FAMILY_TO_EXACT_DIAGNOSIS (CALIBRATION)

## H-03 (FeeManager bad-debt)
- **Exact mechanism recovered?** YES — the increment(global)-vs-set(position) asymmetry across partial liquidations.
- **Runtime-supported?** YES — Tier B, executing the real FeeManagerHelper helpers; residual `totalBadDebtETH` = first
  liquidation amount; corrected reference clears to 0.
- **Scaffold pieces necessary:** the inherit-and-expose-internal harness (`is FeeManagerHelper` + dummy ctor addrs +
  1-fn PositionNFTs mock); public-state reads; a corrected-reference control.
- **What P270 lacked:** it stopped at "bad-debt payback bookkeeping error" — it never instantiated the **two partial
  liquidations + payback** sequence that exposes the overwrite. The missing piece was *multiplicity* (≥2 partials)
  and the *position-overwrite vs global-increment* contrast.
- **Future completion prompts must ask:** "is the position-level accumulator SET or INCREMENTED relative to the
  global? what happens across ≥2 events? does payback deduct cumulative or latest?"

## H-04 (WiseCore liquidation misallocation)
- **Exact mechanism recovered?** YES — the normal-share-sized `potentialPureExtraCashout` granted before the
  `unCollateralized` early-return (branch ordering).
- **Runtime-supported?** YES (Tier C faithful reproduction) — buggy over-extracts by exactly `removePct × userShares`.
- **Scaffold pieces necessary:** faithful transcription of the exact branch ordering + the real cashout formula;
  position-state model; corrected (early-return) control.
- **What P270 lacked:** it stopped at "collateral/share misallocation" — it never traced the **ordering** of the
  uncollateralized check relative to the normal-share cashout. The missing piece was *control-flow ordering*.
- **Future completion prompts must ask:** "for an uncollateralized/special-case position, is the guard checked BEFORE
  or AFTER the value-extraction math? what is the extraction sized by — the gated quantity or an ungated one?"

## Shared lesson → reusable checklist
Both family→exact gaps were **structural/ordering** facts, not deep new discovery: (a) SET-vs-INCREMENT of a
position-vs-global accumulator across repeated events; (b) the ORDER of a special-case guard vs the value math. The
fix for "family-level lending hits" is a **completion checklist** that forces these specific questions before PoC
intent — see LENDING_COMPLETION_CHECKLIST.md. Both were provable at the unit/reproduction tier; a full
deposit→borrow→liquidate runtime was NOT required for these two (a useful, checklist-able finding).
