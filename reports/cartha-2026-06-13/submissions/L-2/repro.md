# Reproduce — L-2 (code analysis, no runnable PoC)

Vulnerable source: `vulnerable/CarthaVault.sol`.
`_update` blocks transfers only while a position is locked → shares are transferable post-lock, but redemption
(`release`/`forceExit`/`processQueuedWithdrawals`) is position-bound with no `redeem(shares)`. Shares transferred to a
non-position address are orphaned (non-redeemable) yet still count in `totalSupply`. See `report.md`. Severity Low. Nothing submitted.
