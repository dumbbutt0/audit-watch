# Optional platform fields (DRAFT — NOT FINAL)

- Title: Permissionless liquidity migration adopts an attacker-pre-created pool, bypassing the intended fee
- Severity (proposed, conservative): Medium
- Affected contract: LiquidityManager (`moveLiquidity` / `addLiquidityToFraxswap`)
- Impact class: lost protocol/LP swap-fee revenue + attacker-controlled migration price
