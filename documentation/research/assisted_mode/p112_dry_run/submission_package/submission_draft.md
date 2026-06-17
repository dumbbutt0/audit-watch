# Permissionless liquidity migration adopts an attacker-pre-created pool, bypassing the intended fee

**Severity: Medium.** Subject: IQ-AI @ `db0d369b`.

## Summary
`LiquidityManager.moveLiquidity` is permissionless and migrates the bootstrap liquidity to Fraxswap via `addLiquidityToFraxswap`, which calls `getPair(currency, agent)` and **adopts any pre-existing pair**, applying the protocol's intended fee only when it has to create the pair. Because `createPair` is permissionless, an attacker can pre-create the `(currency, agent)` pair with an attacker-chosen fee and skewed reserves before migration; the protocol then migrates into the attacker's pool at the attacker's fee.

## Root cause
- `moveLiquidity()` — external, no access control.
- `addLiquidityToFraxswap()` — the pair-exists branch never checks the existing pair's fee equals the intended `fee`, nor that the pair was protocol-created; the intended fee is set only in the create branch.
- `createPair` is permissionless on the external Fraxswap factory.

## Attack scenario
1. An agent's bootstrap pool reaches its end-criterion.
2. An attacker (no protocol role) calls `fraxswapFactory.createPair(currency, agent, lowFee)`.
3. Anyone calls `moveLiquidity()`; the migration adopts the attacker's pair.
4. The live trading pool charges the attacker's fee and started at the attacker's price.

## Impact
The migrated pool charges the attacker's swap fee (**1 bps** in the proof) instead of the intended **100 bps** — roughly 99% of ongoing swap-fee revenue to the agent/LPs is lost for the life of the pool, and the attacker controls the pool's initial price/reserves. Bounded to fee revenue + migration mispricing → **Medium**.

## Recommended mitigation
In the pair-exists branch, reject a pre-existing pair whose fee differs from intent:
```solidity
require((10_000 - fraxswapPair.fee()) == fee, "unexpected pre-existing pair fee");
```
(or restrict pair creation / require the pair be protocol-created, and add slippage/min-out guards to the alignment swaps).
