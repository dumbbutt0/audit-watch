# P104 — Source trace: LiquidityManager.moveLiquidity / addLiquidityToFraxswap

Subject: IQ-AI @ `db0d369b`. Files: `src/LiquidityManager.sol`, `src/BootstrapPool.sol`, `src/AgentFactory.sol`.

## Entry / permissions
- `moveLiquidity()` — **external, no access control** (anyone can trigger migration once the end-criterion holds).
- `initializeBootstrapPool()` — external, guarded only by an `initialized` flag (one-shot, permissionless).
- `fraxswapFactory.createPair(...)` — **permissionless** on the external Fraxswap factory (hardcoded Fraxtal addr).

## Flow (moveLiquidity)
1. `require(!bootstrapPool.killed())`; `price = bootstrapPool.getPrice()` (includes the virtual `phantomAmount`).
2. end-criterion: `reserveCurrency - phantomAmount >= targetCCYLiquidity || >= factory.targetCCYLiquidity()`.
3. `bootstrapPool.kill()` → all real balances move to the LiquidityManager.
4. `currencyAmount = currencyToken.balanceOf(this)`; `liquidityAmount = currencyAmount * 1e18 / price`.
5. `addLiquidityToFraxswap(liquidityAmount, currencyAmount)`.
6. remaining tokens → agent; `factory.setAgentStage(agent, 1)`.

## addLiquidityToFraxswap — the defect
```
fraxswapPair = factory.getPair(currency, agent);
if (fraxswapPair == address(0)) {
    fraxswapPair = factory.createPair(currency, agent, fee);   // intended fee set ONLY here
    ... add liquidity ...
} else {
    // pair already exists: mini-mint + 3 getMaxSell "alignment" swaps + final mint
    // *** no check that this pair's fee == intended `fee`, nor that it was protocol-created ***
}
```
- **Token ordering:** Fraxswap orders internally; not the issue.
- **Migration amount:** `liquidityAmount = currencyAmount*1e18/price` (phantom-influenced) — secondary.
- **Swap rounds:** 3 rounds of `getMaxSell`-sized swaps against the pair to align price; **no slippage/min-out,
  no deadline** — executed against whatever reserves the pair holds.
- **Price assumptions:** only `bootstrapPool.getPrice()`; no external/oracle sanity.
- **External calls:** Fraxswap factory/pair (+ BAMM factory when `shareToBamm>0`).
- **Attacker influence:** an attacker can `createPair(currency, agent, attackerFee)` (and seed skewed reserves)
  **before** anyone calls `moveLiquidity`. The migration then takes the `else` branch and **adopts the
  attacker's pair** — its fee and starting reserves.

## Concrete consequence (reproduced)
The migrated pool uses the **attacker's fee (1 bps)** instead of the protocol's intended **100 bps** → ~99% of
swap-fee revenue to the agent/LPs is lost for the life of the pool; the attacker also dictates the adopted pool's
initial price/reserves (the alignment swaps then trade protocol tokens against attacker-controlled reserves with
no slippage guard). Fee encoding note: Fraxswap `pair.fee()` returns `10_000 - feeBps`.

## Minimal mitigation
In the `else` (pair-exists) branch: `require((10_000 - fraxswapPair.fee()) == fee, "unexpected pre-existing pair
fee")` — reject a pair whose fee ≠ the protocol's intended fee (or restrict pair creation / verify it was
protocol-created). Validated: blocks the attacker pair; clean migration still succeeds.
