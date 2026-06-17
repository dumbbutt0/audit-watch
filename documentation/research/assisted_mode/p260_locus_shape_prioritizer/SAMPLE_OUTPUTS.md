# P260 — SAMPLE_OUTPUTS
Top prioritized loci (score) per contest (top-3) + the award-locus result. Outputs in outputs/<contest>_prioritizer.json.

| contest | top-3 loci (score) | award locus → rank / template / action |
|---|---|---|
| hybra | deposit 30.0 · multiSplit 29.5 · merge 24.5 | **GrowthHYBR.deposit → #1 · T8 · APPLY_RANKING** (the P259 skipped award locus) |
| loopfi | claimFromConverter 23.0 · _withdrawTokens 22.5 · _withdrawExpiredLocksFor 22.0 | CDPVault.liquidatePosition → #13/15 · T7 · APPLY_RANKING |
| sentiment | withdraw 24.0 · liquidate 23.0 · _deposit 23.0 | Pool.rebalanceBadDebt → #6 · T7 · APPLY_RANKING |
| plaza | _redeem 24.5 · _create 23.0 · claim 21.0 | Pool._create → #2 · T8 (+create #6, simulateCreate #15) · APPLY_RANKING |
| bakerfi | deposit 17.0 · rebalance 15.5 · withdraw 15.5 | StrategyLeverage.harvest → #5 · T1 (partial vs fee mechanism) · APPLY_RANKING |
| notional | _mintSharesGivenAssets 23.0 · _burnShares 23.0 · _withdraw 21.5 | _accrueFees → #14 · T6 (collectFees/initiateWithdraw missed) |
| basin | upgradeTo 3.0 · upgradeToAndCall 3.0 · _authorizeUpgrade 1.5 | decodeWellData/calcReserve* → NOT prioritized (math/units shape gap) |

Example mechanism hypothesis (hybra GrowthHYBR.deposit, T8): mechanism_summary "[T8] GrowthHYBR.deposit: external
value movement or supply manipulation may alter share price / proportional claims"; falsification_question "Can a
first-depositor / donation / rounding-to-zero condition skew the share price or claims?"; B/C handoff prepared;
downstream_recommended_action APPLY_RANKING. All hypotheses carry severity:null / concluded:false.
