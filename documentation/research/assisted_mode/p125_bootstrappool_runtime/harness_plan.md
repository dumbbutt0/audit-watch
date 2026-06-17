# P125 — Harness plan & feasibility

**Classification: HARNESS_MODERATE, no fork — REAL pool math.** Uses the iq-ai Foundry project directly (on-disk
`node_modules`: OZ v5, forge-std; solc 0.8.25; `--evm-version cancun`). iq-ai `src/` UNMUTATED; test-only file under
`test/audit/`. The distinguishing feature vs P123/P124: **nothing about the curve/reserves/fee/phantom is mocked** —
the real `BootstrapPool` is deployed and traded; only the two ERC20 tokens are standard mocks (tokens are not the
subject).

## Setup
- `MockLiquidityManager` deploys the pool via `new BootstrapPool(...)` so `BootstrapPool.owner == MockLiquidityManager`
  and `MockLiquidityManager.owner()` returns `feeTo` — satisfying the `sweepFees` fee-routing cast
  `LiquidityManager(owner).owner()`.
- `_freshPool()`: deploy with `initialPrice = 1e18`, `bootstrapAmount = 1_000_000e18`, `feeBps = 100` (1%), then mint
  `1_000_000e18` agent tokens to the pool (bootstrap liquidity). `phantomAmount = 1e24` ⇒ initial reserves `1e24 :
  1e24`, price 1:1, real currency 0 (must be seeded by a buy).
- `MockERC20` (currency, agent) — standard mint/approve/transfer/transferFrom.
- Actors `trader`/`attacker`/`feeTo` = `makeAddr`.

## Probes → `BootstrapPoolInvariantRuntime.t.sol`
- **A round-trip no-profit:** `buy(1000e18)` → `g`; `sell(g)` → `cBack`; assert `cBack < 1000e18`.
- **B constant-product k:** `k = reserveCurrency*reserveAgent` from `getReserves()`; assert `k` non-decreasing after a
  buy and after a sell.
- **C solvency:** seed real currency via a buy; a small sell is honored; a sell quoting more currency than the real
  balance reverts (phantom inflates the quote, not the payout).
- **D sweepFees reserve-neutral:** after a buy accrues a currency fee, an arbitrary caller `sweepFees()`; assert
  `getReserves()` unchanged, fee accumulators zeroed, `feeTo` received exactly the accrued fee.
- **E donation safety:** two identical fresh pools; attacker sells the same `G` agent on each — once with no
  donation (`outNo`), once after donating `Cd` currency (`outYes`); assert `outYes < outNo + Cd` (donation not
  recouped → donor net loss).

## Deps present?
forge-std ✓, OZ v5 ✓ (ReentrancyGuard/SafeERC20/IERC20), solc 0.8.25 ✓, cancun ✓. → MODERATE confirmed; harness built
and runs (see `runtime_matrix.md` / `execution_output.txt`).
