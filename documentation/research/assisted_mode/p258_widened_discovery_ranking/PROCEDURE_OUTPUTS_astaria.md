# astaria — Phase 6: Five-operation completion (PRE-REVEAL, FROZEN)

Ops unchanged; applied to A/B/C winners + top-2-across-≥2-profiles + surviving family-winners.

## A-L1
- **A4 (A-winner, G slope):** STS PASS · IDC PARTIAL (NAV mis-valuation) → PARTIAL_CHAIN.
- **A2 (B/C-winner, C epoch-unsettled):** STS PASS (advance epoch w/ unsettled proxy) · AAS PARTIAL · TSE
  CANDIDATE_STRENGTHENED (LPs stranded / paid from next epoch) · IDC PASS (withdrawReserve conservation broken) → **PARTIAL_CHAIN**.
- A3 (D reentrancy, top-2): STS PASS · TSE PARTIAL → PARTIAL_CHAIN.

## A-L2
- **A1 (A-winner, A interest):** IDC PARTIAL → PARTIAL_CHAIN.
- **A2 (B-winner, G stale-accrual):** STS PASS · IDC CANDIDATE_STRENGTHENED (buyer over/under-pays) → PARTIAL_CHAIN.
- **A3 (C-winner, F wrong-payee):** AAS PASS (attacker buys out, payment misrouted) · CCIT CANDIDATE_STRENGTHENED
  (payee ≠ affected principal) · TSE PASS → **PARTIAL_CHAIN**.

## A-L3
- **A1 (A-winner, A rounding):** dust → NO_CHAIN.
- **A2 (B/C-winner, C future-epoch double-count):** STS PASS · IDC CANDIDATE_STRENGTHENED (withdrawReserve
  double-served) · TSE PASS → **PARTIAL_CHAIN**.

## Summary
| locus | A-winner chain | B-winner chain | C-winner chain |
|---|---|---|---|
| A-L1 | PARTIAL (slope) | PARTIAL (epoch) | PARTIAL (epoch) |
| A-L2 | PARTIAL (interest) | PARTIAL (stale-accrual) | PARTIAL (payee) |
| A-L3 | NO_CHAIN (dust) | PARTIAL (future-epoch) | PARTIAL (future-epoch) |

**FREEZE** before key opened; hashes in REVEAL_AND_SCORE_astaria.md.
