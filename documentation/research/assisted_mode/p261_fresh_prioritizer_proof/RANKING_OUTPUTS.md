# P261 — RANKING_OUTPUTS (Profile B / Profile C on P260 mechanisms; PRE-REVEAL; UNSCORABLE — no key)
## S1 sUSDM.cooldownShares
- Profile B winner: T6 cross-tx-drift (usdmAmount locked at cooldown-rate vs later totalAssets/yield → claim
  mismatch / pending-claims drift); top-2 T6,T2. Profile C winner: T2 redemption-state-coupling (escrow/
  totalPendingClaims accounting on burn); top-2 T2,T6. B≠C. falsifier: claim pays at claim-time rate not locked rate.
## S2 MonetrixVault.claimRedeem
- B winner: T1 external-dependency (redemption funding/escrow availability can block claim — DoS); C winner: T1
  (same); top-2 T1,T2. falsifier: claim is always fully funded before enabling.
## S3 MonetrixVault.distributeYield
- B winner: T6 cross-epoch yield drift; C winner: T5 terminality (distribution leaves a state blocking later
  distribution); top-2 T6,T5. B≠C. falsifier: distribution is idempotent/period-guarded.
## S4 MonetrixVault.deposit
- B/C winner: T8 share-price — **REFUTED pre-reveal** (1:1 USDC→USDM mint, no share price) → NO_CHAIN expected.
FREEZE.
