# P125 — Candidate selection (cross-contract pivot)

**Research-only / un-wired.** This phase is a **user-directed cross-contract pivot**, not the mechanical
next-permissionless pick.

## Rationale
P120–P124 produced five consecutive novel KILLs whose shared lesson is: top-ranked permissionless entrypoints are
router/wrapper/guarded surfaces **sound at their own level**, while the real economic risk (when any) lives
**cross-contract** in the delegated pricing/accounting. P123 (`AgentRouter.buy`) and P124 (`AgentRouter.sell`)
explicitly deferred `BootstrapPool` pricing as NEEDS_CONTEXT. P125 targets exactly that deferred frontier.

## Target
`iq-ai-2025-01 :: BootstrapPool` — the bonding-curve pricing engine behind both `AgentRouter` (the routers call
`bootstrapPool.buy/sell/getAmountOut`) and `LiquidityManager.moveLiquidity` (which reads/migrates pool reserves at
`kill()`). Its permissionless surface: `buy`, `sell`, `getAmountOut`/`getAmountIn`, `getPrice`, `getReserves`,
`sweepFees`. The harness exercises the **real curve math** — only the standard ERC20 tokens are mocked.

## Novelty check
iq-ai awarded set = `LiquidityManager.moveLiquidity` (IQ-M-01) + `AgentFactory` (IQ-H-01).
`BootstrapPool` is **not** awarded → genuinely novel.

## Why this breaks the prior ceiling
P123/P124 mocked the pool to prove the routers were thin/safe but could not (honestly) judge the pool's pricing.
P125 deploys the **real** `BootstrapPool` and tests its economic invariants directly — the first cross-contract
pricing harness in this arc, materially beyond the thin-router KILLs.
