# P123 — Harness plan & feasibility

**Classification: HARNESS_MODERATE, no fork.** Uses the iq-ai Foundry project directly (full on-disk `node_modules`:
OZ v5, dev-fraxswap, forge-std; solc 0.8.25; `--evm-version cancun` required — OZ uses `mcopy`, per P104). iq-ai
`src/` is UNMUTATED; the harness is a test-only file under `test/audit/` (mirrors P118's secondswap `test/audit/`).

## Why mockable despite concrete-typed collaborators
`AgentRouter`'s constructor takes `AgentFactory` (a concrete type), and `buy` casts `LiquidityManager(...)` /
`BootstrapPool(...)`. Solidity allows `AgentFactory(address(mock))` (address→contract-type cast); calls dispatch by
selector. So every collaborator is replaced by a mock implementing just the called selectors:
| Mock | Selectors |
|---|---|
| `MockAgentFactory` | `currencyToken()`, `tokenAgent(address)`, `agentManager(address)`, `setAgent(...)` |
| `MockLiquidityManager` | `bootstrapPool()` |
| `MockBootstrapPool` | `killed()`, `buy(uint256,address)` (pull currency via `transferFrom`, send agent token to recipient, return quote), `getAmountOut` |
| `MockERC20` ×2 | currency + agent token |
| `MockFraxswapPair` | `sync()`, `getAmountOut(uint256,address)`, `token0()`, `swap(uint256,uint256,address,bytes)` |
| `MockFraxswapFactory` | `getPair(address,address)`, `setPair(...)` |

## Fraxswap branch (killed path)
`fraxswapFactory` is a hardcoded constant `0xE30521…`. The harness deploys `MockFraxswapFactory`, `vm.etch`-es its
runtime code at the constant address, then calls `setPair(currency, agent, pair)` on it (etch copies code; storage is
set via the post-etch call). `MockBootstrapPool.killed()` returns true → the router takes the Fraxswap branch.

## Deploy / setup
`router = new AgentRouter(AgentFactory(address(mockFactory)))` (constructor reads `mockFactory.currencyToken()`).
`_wireBootstrap(killed, quote)` deploys the mock pool (pre-funded with agent tokens) + a mock LM and registers the
agent in the factory. `buyer`/`recipient` = `makeAddr`.

## Test matrix (Cases A–E) → `AgentRouterBuyRuntime.t.sol`
- **A** `tokenAgent == 0` → revert `AgentNotFound`.
- **B** bootstrap happy path → router pulls exactly `_amountIn`; `bootstrapPool.buy` receives `_amountIn` + recipient;
  recipient gets `quote`; router holds 0 of both tokens; buyer paid exactly `_amountIn`.
- **C** `_minAmountOut > quote` → revert `InsufficientAmountOut`.
- **D** `recipient != buyer` → recipient gets tokens, buyer pays, buyer gets nothing.
- **E** Fraxswap killed path (etched factory/pair) → `_amountIn` routed to the pair, `quote` to the recipient,
  `_minAmountOut` enforced, router holds 0.

## Deps present?
forge-std ✓, OZ v5 ✓, dev-fraxswap ✓ (node_modules), solc 0.8.25 ✓, cancun ✓. → MODERATE confirmed; harness built
and runs (see `runtime_matrix.md` / `execution_output.txt`).
