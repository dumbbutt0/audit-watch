# plaza — Phase 2: Mechanism Selection Gate (PRE-REVEAL, FROZEN)

3 subtle loci (all BASE_BORN_INCOMPLETE; ≥3 plausible mechanisms each; no typo/missing-revert/single-mechanism).
8-dim scores H/M/L: controllability · value-delta · victim/gainer · comparand · terminality · amplification ·
simplicity · award-likeness.

---
## P-L1 — `Pool.getCreateAmount`/`getRedeemAmount` collateral-level pricing
**No-hindsight lock:** selected for the protocol's core bond/leverage pricing invariant; signal = accounting A4/A2
on _create/_redeem + ST on create/redeem; base saw the create-uses-current vs redeem-BOND-uses-post-supply basis;
remained incomplete = which divergence is exploitable and by whom.
Mechanisms enumerated (4):
- **M1 create/redeem collateralLevel BASIS asymmetry** — redeem-BOND recomputes collateralLevel with post-redemption `(bondSupply-depositAmount)` while create/leverage use current supply ⇒ a redeemer near the threshold lands in a different rate branch than symmetric create ⇒ round-trip / boundary value extraction. [ctrl H · delta M · v/g H · comparand H(create is the sibling) · terminality M · amp H(repeat) · simplicity M · award-like H]
- **M2 threshold discontinuity arb** — at `collateralLevel == COLLATERAL_THRESHOLD` creation/redeem rate jumps between formulas ⇒ push pool across threshold then create/redeem. [ctrl M · delta M · v/g M · comparand M · term M · amp M · simpl L · award M]
- **M3 marketRate one-sided cap** — bond redeem capped by `marketRate` but create is not ⇒ create-high/redeem-capped asymmetry. [ctrl M · delta M · v/g M · comparand M · term L · amp M · simpl M · award M]
- **M4 leverage redeemRate underflow** `(tvl - bondSupply*BOND_TARGET_PRICE)` — REFUTED (guarded by collateralLevel branch).
- `SELECTED_MECHANISM`: **M1 basis asymmetry**. `RUNNER_UP`: **M2 threshold discontinuity**. `REFUTED`: M4 (guarded); M3 demoted (one-sided cap is likely intended protection).
- `AWARDED_LIKENESS_REASON`: pricing-basis inconsistency between sibling create/redeem is a classic AMM/derivative mispricing award shape.
- `WHY_SELECTED_OVER_RUNNER_UP`: M1 has a concrete sibling comparand (create) and clear who-wins (redeemer), higher controllability than pushing the pool across a threshold (M2 needs capital to move collateralLevel).
- `WHAT_WOULD_FALSIFY`: if post-supply basis in redeem is provably the intended/correct level (matches a documented invariant) and round-trips net ≤ fees, M1 is void.

## P-L2 — `Pool` time-fee subtracted in pricing only
**No-hindsight lock:** selected because priced reserves ≠ real balance is a reconciliation hazard; signal = A2
conservation on simulate*/_redeem; base saw the fee subtracted in pricing but transfers use full balance; remained
incomplete = whether the gap is extractable.
Mechanisms (3):
- **M1 fee-not-segregated reconciliation gap** — accrued fee reduces priced reserves every create/redeem but is never moved out; `claimFees` later mints/transfers the fee from real balance ⇒ if users already redeemed against reduced pricing, the protocol's claimable fee and the reserve backing diverge ⇒ last redeemers / fee recipient shortchanged. [ctrl M · delta M · v/g M · comparand M · term M · amp M · simpl M · award M]
- **M2 fee double-charge across period** — every tx recomputes fee from `lastFeeClaimTime` over current reserves without resetting it ⇒ the same elapsed fee is repeatedly priced in. [ctrl M · delta H · v/g M · comparand M · term M · amp H · simpl M · award M]
- **M3 fee-on-growing-reserves** — fee = reserves*rate*Δt; as reserves grow the historical Δt is charged at the new (larger) reserve ⇒ over-charge. [ctrl L · delta M · v/g M · comparand L · term L · amp M · simpl M · award L]
- `SELECTED_MECHANISM`: **M2 repeated fee pricing (double-charge over the un-reset period)**. `RUNNER_UP`: **M1 reconciliation gap**. `REFUTED`: none (M3 demoted as a subset of M2).
- `AWARDED_LIKENESS_REASON`: fee computed against `block.timestamp - lastFeeClaimTime` but not reset on each pricing call is a recognized "fee charged repeatedly / users overpay" shape.
- `WHY_SELECTED_OVER_RUNNER_UP`: M2 has the clearest measurable value-delta (users systematically priced worse) and amplifies every tx; M1 needs a specific claimFees-ordering to bite.
- `WHAT_WOULD_FALSIFY`: if the fee subtraction is purely a *view*-side conservative estimate that `claimFees` reconciles exactly (no user pays twice), M2 is void.

## P-L3 — `Pool.startAuction` coupon snapshot + `transferReserveToAuction`
**No-hindsight lock:** selected for coupon distribution accounting across a changing supply; signal = ST on
auction + A on BondToken indexing; base saw the snapshot couponAmount; remained incomplete = over/under-distribution path.
Mechanisms (3):
- **M1 coupon snapshot vs changing supply** — `couponAmountToDistribute = totalSupply*sharesPerToken` at start, but bonds mint/burn during the period and `increaseIndexedAssetPeriod` indexes per-share ⇒ claimers may exceed/undershoot the snapshot coupon. [ctrl M · delta M · v/g M · comparand M · term M · amp M · simpl M · award M]
- **M2 poolSaleLimit over-drain** — auction can pull up to `poolSaleLimit` of reserves; a high limit lets an auction drain reserves backing bonds ⇒ undercollateralization. [ctrl M · delta H · v/g H · comparand M · term H · amp M · simpl M · award H]
- **M3 indexed-period coupon double/loss on redeem-during-auction** — redeeming bonds mid-period may forfeit or double-count coupon shares. [ctrl M · delta M · v/g M · comparand M · term M · amp M · simpl L · award M]
- `SELECTED_MECHANISM`: **M2 poolSaleLimit reserve over-drain (undercollateralization)**. `RUNNER_UP`: **M1 coupon snapshot drift**. `REFUTED`: none (M3 demoted).
- `AWARDED_LIKENESS_REASON`: an auction draining reserves that back bondholders is a direct fund-loss/undercollateralization shape (High-like).
- `WHY_SELECTED_OVER_RUNNER_UP`: M2 has the clearest victim/gainer and terminality (reserves gone) and higher severity; M1 is a softer distribution drift.
- `WHAT_WOULD_FALSIFY`: if `poolSaleLimit`/`endAuction` enforces an undercollateralization-safe cap, M2 is void.

**FREEZE:** selections final before completion + reveal.
