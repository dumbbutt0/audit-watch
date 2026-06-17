# P261 — PROCEDURE_OUTPUTS (five ops; PRE-REVEAL; UNSCORABLE — frozen for deferred reveal)
Unchanged STS/AAS/TSE/IDC/CCIT on B/C winners. NOTE: no answer key → these are pre-reveal hypotheses only; no
recovery is claimed (Phase-6 reveal UNAVAILABLE).
## S1 sUSDM.cooldownShares (B=T6 rate-drift / C=T2 escrow-accounting)
- STS PASS (cooldown burns shares, locks usdmAmount at current rate, escrow.deposit) · AAS PARTIAL (timing around
  yield/rate change) · TSE PARTIAL (claim pays locked amount) · IDC CANDIDATE_STRENGTHENED (locked-rate vs realized
  yield delta; totalPendingClaims) · CCIT NO_EFFECT → PARTIAL_CHAIN (hypothesis).
## S2 MonetrixVault.claimRedeem (T1 funding-availability)
- STS PASS · AAS PARTIAL · TSE CANDIDATE_STRENGTHENED (claim blocked if redemptions unfunded) · IDC PARTIAL → PARTIAL_CHAIN (hypothesis).
## S3 MonetrixVault.distributeYield (T6/T5)
- STS PASS · IDC PARTIAL (cross-epoch drift) · TSE PARTIAL → PARTIAL_CHAIN (hypothesis).
## S4 MonetrixVault.deposit (T8)
- STS PASS · IDC NO_EFFECT (1:1 mint, no share price) → **NO_CHAIN / REFUTED** (honest: T8 over-fired).
## Summary: 3 PARTIAL_CHAIN hypotheses (S1/S2/S3) + 1 REFUTED (S4). ALL UNSCORED (reveal unavailable). FREEZE.
