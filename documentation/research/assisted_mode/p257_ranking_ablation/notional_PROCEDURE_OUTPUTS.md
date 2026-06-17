# notional — Phase 5: Five-operation completion (PRE-REVEAL, FROZEN)

Ops unchanged; applied to Profile-A winner, Profile-B winner, Profile-C winner, and common runner-up (M3) per locus.

## N-L1
- **A-winner M1 (virtual-share rounding):** STS PASS / IDC dust / TSE L → **NO_CHAIN** (dust).
- **B/C-winner M2 (escrow recon):** STS PASS (escrow leaves supply, yield tokens stay) · AAS PARTIAL (size a
  withdraw, convert during window) · IDC CANDIDATE_STRENGTHENED (remaining-holder conversion inflated by escrowed
  yield tokens) · TSE PASS (value redistributed) · CCIT NO_EFFECT → **PARTIAL_CHAIN**.
- runner-up M3 (NAV drift): IDC PARTIAL → PARTIAL_CHAIN.

## N-L2
- **A-winner M1 (approx error):** IDC dust → **NO_CHAIN**.
- **B/C-winner M2 (fee-accrue dodge):** STS PASS · AAS PARTIAL (choose entry path/timing) · IDC
  CANDIDATE_STRENGTHENED (mint at stale-fee price) · TSE PARTIAL · CCIT NO_EFFECT → **PARTIAL_CHAIN**.
- runner-up M3: IDC PARTIAL → PARTIAL_CHAIN.

## N-L3
- **A-winner M1 (transient stale):** STS PASS · TSE PARTIAL → **PARTIAL_CHAIN** (needs an unclear-clear path).
- **B/C-winner M2 (escrow desync):** STS PASS (escrow add w/o idempotency) · AAS PARTIAL · IDC
  CANDIDATE_STRENGTHENED (effectiveSupply understated → conversion inflated) · TSE PASS (persistent desync) → **PARTIAL_CHAIN**.
- runner-up M3 (withdraw-request bypass): TSE PARTIAL → PARTIAL_CHAIN.

## Summary (frozen)
| locus | A-winner chain | B/C-winner chain |
|---|---|---|
| N-L1 | NO_CHAIN (dust) | PARTIAL_CHAIN (escrow recon) |
| N-L2 | NO_CHAIN (dust) | PARTIAL_CHAIN (fee dodge) |
| N-L3 | PARTIAL_CHAIN | PARTIAL_CHAIN (escrow desync) |

Note: the messy B/C mechanisms complete to PARTIAL_CHAIN; the tidy A mechanisms mostly NO_CHAIN (dust) — a
pre-reveal sign that B/C surface the more *consequential* mechanism. **FREEZE** before key opened.
