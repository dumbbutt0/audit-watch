# Minimal reproduction hypothesis

Candidate: `wildcat-2024-08 :: WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches`.

## Source-backed hypothesis attempt

Read WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches. It is `public nonReentrant sphereXGuardExternal`; calling it pulls the caller's assets in (safeTransferFrom) to repay debt and then processes unpaid batches with `satSub`-guarded available-liquidity accounting — i.e. calling it DONATES funds, not extracts them. Any real issue would be inside `_processUnpaidWithdrawalBatch`'s pro-rata math (the awarded executeWithdrawal class), which cannot be confirmed or refuted from source alone. No source-provable exploit; not provably safe. Truthful terminal: NEEDS_CONTEXT.

## What runtime evidence would be required

A falsifiable runtime check could not be specified from source alone for this candidate (see rationale). Resolving it would require execution-backed evidence — e.g. a fork/local deployment plus a differential or invariant test across the cross-contract boundary named above — not further source reasoning. Absent that, the truthful terminal is `NEEDS_CONTEXT`; no exploit is claimed and no finding is promoted.
