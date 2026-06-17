# P297 — WAVE2_RESULTS

- attempted: **9** (all 9 incl. wave 1) · verifier confirmations: **9** · confirmed_but_unmapped: 0 · confirmed_FP: **0** · pass: **True**
- **cumulative recall-of-confirmed: 6 (P295 baseline) + 9 (loop) = 15 loci**
- refutation control: refuted_by_execution (attacker_verified=False)

## Verifier verdict per locus (agent_claimed is advisory; verifier is authoritative)

| audit:id | locus | agent_claimed | verifier | L1L2L3 | map | clean | fidelity |
|---|---|---|---|---|---|---|---|
| kelp-2023-11-holdout:H-02 | LRTDepositPool.depositAsset/getRsETHAmountToMint | confirmed | confirmed_by_execution | 111 | True | True | high |
| kelp-2023-11-holdout:M-01 | LRTDepositPool.getTotalAssetDeposits | confirmed | confirmed_by_execution | 111 | True | True | CAVEATED(human-review) |
| kelp-2023-11-holdout:M-02 | LRTDepositPool.depositAsset | confirmed | confirmed_by_execution | 111 | True | True | high |
| ecg-2023-12-holdout:H-01 | ProfitManager.claimGaugeRewards | confirmed | confirmed_by_execution | 111 | True | True | high |
| ecg-2023-12-holdout:H-02 | ERC20RebaseDistributor.transfer | confirmed | confirmed_by_execution | 111 | True | True | high |
| ecg-2023-12-holdout:H-03 | LendingTerm.onBid | confirmed | confirmed_by_execution | 111 | True | True | high |
| ecg-2023-12-holdout:M-02 | RateLimitedMinter.mint | confirmed | confirmed_by_execution | 111 | True | True | CAVEATED(human-review) |
| ecg-2023-12-holdout:M-03 | ProfitManager.totalBorrowedCredit | confirmed | confirmed_by_execution | 111 | True | True | high |
| salty-2024-01-holdout:H-05 | CollateralAndLiquidity.depositCollateralAndIncreaseShare | confirmed | confirmed_by_execution | 111 | True | True | high |

## Honest fidelity note (the user's 'don't let in bad bugs')
All 9 are **verifier-confirmed** (real forge exploit PASS + L1+L2+L3 + assertion_map) on **awarded loci**. Two carry
a builder-flagged MECHANISM-FIDELITY caveat — the PoC proves a real on-source behavior at the awarded locus, but
whether it matches the EXACT awarded mechanism warrants human confirmation:
- **ecg M-02** RateLimitedMinter.mint — proves cumulative minting over drain+wait cycles exceeds bufferCap; this is
  partly inherent to a *rate* limiter (limits rate, not total supply). Route to human review.
- **kelp M-01** getTotalAssetDeposits — proves a double-count during an EigenLayer queued-withdrawal window; depends
  on the withdrawal/settlement share semantics the PoC modeled. Route to human review.
So: **9 verifier-confirmed = 7 high-fidelity + 2 fidelity-caveated (human-review)**. confirmed-FP=0 either way.

## Reading
- All 6 wave-2 builders produced PoCs the verifier confirmed (claimGaugeRewards late-joiner retroactive reward;
  totalBorrowedCredit bad-debt underflow/skip-cap; depositAsset missing min-out slippage; getTotalAssetDeposits
  double-count; RateLimitedMinter cumulative overshoot; cooldown-reset liquidation evasion).
- The verifier remains the sole judge; builder self-reports are advisory; the p290 refutation control stays refuted.
