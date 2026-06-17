# ethos — Phase 6: Five-operation completion (PRE-REVEAL, FROZEN)

Ops unchanged; applied to A/B/C winners + top-2-across-≥2-profiles + surviving family-winners.

## E-L1
- **E1 (A-winner, profit recalc):** IDC PARTIAL → PARTIAL_CHAIN.
- **E2 (B/C-winner, ERC4626 convexity):** STS PASS · AAS PARTIAL (manip yield-vault share price / donation) · IDC
  CANDIDATE_STRENGTHENED (phantom profit / under-withdraw → SP & stakers lose) · TSE PASS (collateral shortfall) → **PARTIAL_CHAIN**.
- E3 (E rounding, top-2): IDC PARTIAL → PARTIAL_CHAIN.

## E-L2
- **E1 (A-winner, rounding):** dust → NO_CHAIN.
- **E2 (B/C-winner, scale/epoch drift):** STS PASS · IDC CANDIDATE_STRENGTHENED (depositor reward mis-credit across
  scale change) · TSE PARTIAL → **PARTIAL_CHAIN**.

## E-L3
- **E4 (A-winner, base-rate):** IDC dust → NO_CHAIN.
- **E2 (B-winner, C reInsert mis-sort):** STS PASS · TSE CANDIDATE_STRENGTHENED (trove stranded / redemption skips) → **PARTIAL_CHAIN**.
- **E3 (C-winner, F cross-collateral identity):** AAS PASS · CCIT CANDIDATE_STRENGTHENED (redeemer vs owner vs
  collateral binding) · TSE PASS → **PARTIAL_CHAIN**.

## Summary
| locus | A-winner | B-winner | C-winner |
|---|---|---|---|
| E-L1 | PARTIAL (recalc) | PARTIAL (convexity) | PARTIAL (convexity) |
| E-L2 | NO_CHAIN (dust) | PARTIAL (scale-drift) | PARTIAL (scale-drift) |
| E-L3 | NO_CHAIN (dust) | PARTIAL (reInsert) | PARTIAL (identity) |

**FREEZE** before key opened; hashes in REVEAL_AND_SCORE_ethos.md.
