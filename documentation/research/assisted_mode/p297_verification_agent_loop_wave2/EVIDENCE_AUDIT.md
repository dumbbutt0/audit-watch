# P297 — EVIDENCE_AUDIT

Each wave-2 confirmation = a real forge exploit PASS (L1+L2+L3) + an assertion_map; audited for mechanism fidelity.

## High-fidelity confirmations (mechanism faithful to a real bug at the awarded locus)
- **ecg H-01 ProfitManager.claimGaugeRewards** — REAL defect found by the builder (better than the hint):
  `claimGaugeRewards` early-returns `if (_userGaugeWeight == 0) return 0;` BEFORE writing `userGaugeProfitIndex`, and
  `GuildToken._incrementGaugeWeight` calls it while the new voter's weight is still 0 → the new voter's index is
  never checkpointed → `deltaIndex = gaugeProfitIndex - 1e18` pays them on profit accrued before they joined. L2:
  named `userGaugeProfitIndex` stays 0; L3: bob earns 100e18 vs entitled 0; control checkpoints → 0. FAITHFUL.
- **ecg M-03 ProfitManager.totalBorrowedCredit** — `targetTotalSupply() - SimplePSM.redeemableCredit()` where
  `redeemableCredit` is recomputed at the CURRENT creditMultiplier; bad debt lowers the multiplier → redeemableCredit
  inflates → total understates, and once it exceeds targetTotalSupply the subtraction UNDERFLOWS/reverts. Downstream:
  LendingTerm.debtCeiling/_borrow consume it → either skip the proportional cap (over-issue) or DoS. L2/L3 named +
  asserted, control clean. FAITHFUL (real downstream impact, verbatim control-flow).
- **kelp M-02 LRTDepositPool.depositAsset** — no `minRSETHAmountExpected` / min-out check on the mint path; a price
  move between quote and execution mints fewer rsETH with NO revert. L2: quotedOut 100e18 vs actualOut 80e18; L3:
  assertLt + the call did not revert; control with a min-out guard reverts. FAITHFUL (clearly-missing guard).
- **salty H-05 CollateralAndLiquidity.depositCollateralAndIncreaseShare** — builder VERIFIED in source that
  `liquidateUser` → `_decreaseUserShare(wallet,...,useCooldown=true)` does `require(block.timestamp >=
  user.cooldownExpiration)` on the LIQUIDATEE, and `depositCollateralAndIncreaseShare` → `_increaseUserShare` re-arms
  `cooldownExpiration`. So a borrower re-arms their cooldown to make liquidation revert. L2: cooldownExpiration /
  canLiquidate before/after; L3: liquidation reverts while canUserBeLiquidated==true; control: succeeds after lapse.
  FAITHFUL (the cooldown gate on liquidation is real in source).
- (wave 1, re-judged) **kelp H-02, ecg H-02, ecg H-03** — audited in P296 EVIDENCE_AUDIT; faithful.

## Fidelity-caveated confirmations (verifier-confirmed; route to human review)
- **ecg M-02 RateLimitedMinter.mint** — the PoC truthfully shows `buffer()` is `min(stored + rate*elapsed, cap)` and
  drain+wait+drain mints `3*bufferCap` cumulatively (asserted `totalMinted > bufferCap`). The builder HONESTLY flagged
  that a *rate* limiter emitting more than bufferCap over real time is partly BY DESIGN — so the awarded M-02 may be a
  different/narrower accounting concern. Verifier-confirmed (execution real) but **mechanism fidelity uncertain →
  human review**. Not counted as a clean awarded-mechanism match without that review.
- **kelp M-01 LRTDepositPool.getTotalAssetDeposits** — the PoC shows a 100% double-count when an EigenLayer
  queued-withdrawal returns custody to the NDC while `userUnderlyingView` is not yet zeroed (both legs count the same
  tokens). This depends on the modeled withdrawal/settlement share semantics. Verifier-confirmed but the
  window-assumption **warrants human review** against the real EigenLayer integration.

## Cross-cutting
- **confirmed-FP = 0** — verifier is the sole confirmer; the p290 refutation control stays refuted; no
  confirmed_but_unmapped; every clean confirmation has a real log + assertion_map.
- **Verifier-authoritative** — builder self-reports (all 9 "confirmed") are advisory; the verifier independently
  re-ran forge + L1/L2/L3 on each. The override path (a "confirmed" claim on a FAILING exploit → not confirmed) is
  proven by the synthetic test.
- **Honest distinction surfaced:** verifier-confirmation proves EXECUTION, not exact awarded-mechanism fidelity — the
  assertion_map + a human-review tier handle the residual (2/9 here).
