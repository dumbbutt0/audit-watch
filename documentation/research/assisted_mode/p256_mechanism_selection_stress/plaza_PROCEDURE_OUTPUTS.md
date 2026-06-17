# plaza — Phase 3: Five-operation completion on SELECTED + RUNNER-UP (PRE-REVEAL, FROZEN)

Ops unchanged (STS/AAS/TSE/IDC/CCIT); labels PASS/NO_EFFECT/UNCLEAR/CANDIDATE_STRENGTHENED; chain status.

## P-L1 — SELECTED M1 (create/redeem collateralLevel basis asymmetry)
- STS PASS (redeem-BOND collateralLevel uses post-supply; create uses current → different branch near threshold).
- AAS PASS (attacker sizes deposit/redeem to straddle the threshold). TSE PARTIAL (value shifts between token classes/redeemer & pool). IDC CANDIDATE_STRENGTHENED (rate basis differs ⇒ redeemer can realize a better-than-fair rate). CCIT NO_EFFECT.
- **Chain status: PARTIAL_CHAIN.** Runner-up M2 (threshold discontinuity): STS PASS / IDC PARTIAL → PARTIAL_CHAIN (needs capital to move level).

## P-L2 — SELECTED M2 (repeated fee pricing over un-reset period)
- STS PASS (each create/redeem recomputes fee from lastFeeClaimTime, not reset). AAS NO_EFFECT (affects all users). TSE PARTIAL. IDC CANDIDATE_STRENGTHENED (users systematically priced worse than the single accrued fee). CCIT NO_EFFECT.
- **Chain status: PARTIAL_CHAIN.** Runner-up M1 (reconciliation gap): IDC PARTIAL → PARTIAL_CHAIN.

## P-L3 — SELECTED M2 (poolSaleLimit reserve over-drain)
- STS PASS (auction pulls reserves up to poolSaleLimit). AAS PARTIAL (auction is permissioned-ish; bidder/keeper). TSE CANDIDATE_STRENGTHENED (reserves leave the pool → bonds undercollateralized terminal state). IDC PASS (reserve delta vs bond backing). CCIT NO_EFFECT.
- **Chain status: PARTIAL_CHAIN.** Runner-up M1 (coupon snapshot drift): IDC PARTIAL → PARTIAL_CHAIN.

## Summary (frozen)
| locus | selected | runner-up | selected chain |
|---|---|---|---|
| P-L1 | M1 basis asymmetry | M2 threshold | PARTIAL |
| P-L2 | M2 repeated fee | M1 reconciliation | PARTIAL |
| P-L3 | M2 saleLimit drain | M1 coupon snapshot | PARTIAL |

**FREEZE** before key opened; hashes in plaza_REVEAL_AND_SCORE.md.
