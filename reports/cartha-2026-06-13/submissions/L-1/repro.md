# Reproduce — L-1 (code analysis, no runnable PoC)

Vulnerable source: `vulnerable/CarthaParentVault.sol`.
Inspect `withdraw`, `releaseFromParent`, `processQueuedParentWithdrawals`, `_prepareSharePayout`, `_withdrawFromChildren`:
full (`roundUp` / `lockedShares`) share burn vs `payout = min(value, balance)` after a single-pass, per-child-floored
`_withdrawFromchildren`, guarded only by a `+10` wei tolerance → bounded dust underpayment to the withdrawer.
See `report.md`. Severity Low (dust). Nothing submitted.
