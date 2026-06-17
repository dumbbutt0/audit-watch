# P261 — PRIORITIZER_OUTPUT (frozen P260 module on FRESH monetrix; PRE-REVEAL)
Ran `scripts/research/locus_shape_prioritizer.py` (UNCHANGED from P260) on the fresh monetrix manifest + checkpoints.
NO answer key. candidate-loci 66 → bounded top-15 (no flood). Full JSON: outputs/monetrix_prioritizer.json.

| rank | contract.function | score | templates | top-2 | action |
|---|---|---|---|---|---|
| 1 | sUSDM.cooldownShares | 23.0 | T2,T5 | T2,T5 | APPLY_RANKING |
| 2 | sUSDM.cooldownAssets | 23.0 | T2,T5 | T2,T5 | APPLY_RANKING |
| 3 | IMonetrixConfigReader.tradeableAssets | 19.0 | T6 | T6 | APPLY_RANKING |
| 4 | IMonetrixConfigReader.spotToPerp | 19.0 | T6 | T6 | APPLY_RANKING |
| 5 | IMonetrixConfigReader.isSpotWhitelisted | 18.5 | T6 | T6 | APPLY_RANKING |
| 6 | InsuranceFund.withdraw | 17.5 | T2 | T2 | APPLY_RANKING |
| 7 | MonetrixVault.distributeYield | 14.5 | T5,T6 | T6,T5 | APPLY_RANKING |
| 8 | MonetrixVault.claimRedeem | 13.5 | T1,T2,T5 | T1,T2 | APPLY_RANKING |
| 9 | MonetrixVault.deposit | 13.0 | T5,T8 | T8,T5 | APPLY_RANKING |
| 10 | MonetrixVault.settle | 13.0 | T1,T2,T5 | T1,T2 | APPLY_RANKING |
| 11 | MonetrixVault.fundRedemptions | 12.5 | T5 | T5 | APPLY_RANKING |
| 12 | MonetrixVault.emergencyBridgePrincipalFromL1 | 12.0 | T4 | T4 | APPLY_RANKING |

Observations (pre-reveal, operational): the module surfaced the genuine subtle-accounting loci of a synthetic-dollar
protocol on top — staked-share cooldown (sUSDM), insurance-fund withdrawal, yield distribution, redemption funding,
cross-chain emergency bridge — bounded, B/C-ready, 0 severity/concluded. Precision caveats: #3–#5 are
`IMonetrixConfigReader` view getters (interface T6-keyword over-fire, lower value); #9 Vault.deposit routed T8 but
is a 1:1 USDC→USDM mint (no share price) → T8 over-fire (the real share-price surface is sUSDM, #1/#2). FREEZE.
