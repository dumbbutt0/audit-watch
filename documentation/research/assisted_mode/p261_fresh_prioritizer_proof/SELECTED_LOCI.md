# P261 — SELECTED_LOCI (from P260 output; PRE-REVEAL)
4 loci from the prioritizer (≥1 T7/T8, ≥1 of T1–T6; prefer genuine subtle over interface getters).
- **S1 sUSDM.cooldownShares (#1; T2,T5)** — why: staked-share unstake locks `usdmAmount = convertToAssets(shares)`
  at cooldown-time rate + `totalPendingClaims`/escrow; subtle rate/yield-timing + pending-claims accounting.
- **S2 MonetrixVault.claimRedeem (#8; T1,T2,T5)** — why: redemption claim depends on escrow/redemption funding
  availability (T1 external-dep) + withdrawal state-coupling (T2).
- **S3 MonetrixVault.distributeYield (#7; T5,T6)** — why: yield distribution drift across epochs / terminality (T5/T6).
- **S4 MonetrixVault.deposit (#9; T8)** — included to satisfy ≥1 T7/T8; **caveat: 1:1 USDC→USDM mint (no share
  price) → T8 likely over-fired here; real share-price surface is sUSDM (S1).** Recorded honestly.
Skipped high-ranked: #3–#5 IMonetrixConfigReader getters (interface view over-fire, low value); MonetrixVault.settle
(#10, similar to claimRedeem). FREEZE.
