# P124 — Harness plan & feasibility

**Classification: HARNESS_MODERATE, no fork.** Reuses the P123 setup exactly: the iq-ai Foundry project directly
(on-disk `node_modules`: OZ v5, dev-fraxswap, forge-std; solc 0.8.25; `--evm-version cancun`, OZ `mcopy`). iq-ai
`src/` UNMUTATED; test-only file under `test/audit/`.

## Mocks (collaborators address-cast-mocked via selector dispatch — `AgentRouter(AgentFactory(address(mock)))`)
| Mock | Selectors |
|---|---|
| `MockAgentFactory` | `currencyToken()`, `tokenAgent(address)`, `agentManager(address)`, `setAgent(...)` |
| `MockLiquidityManager` | `bootstrapPool()` |
| `MockBootstrapPool` | `killed()`, **`sell(uint256,address)`** (pull AGENT token via `transferFrom`, send CURRENCY to recipient, return quote), `getAmountOut` |
| `MockERC20` ×2 | currency + agent token |
| `MockFraxswapPair` | `sync()`, `getAmountOut(uint256,address)`, `token0()`, **`swap`** (delivers CURRENCY out) |
| `MockFraxswapFactory` | `getPair`, `setPair` (etched at `0xE305…`) |

The only delta vs P123 (`buy`): the pool/pair pay out CURRENCY for AGENT-token input (opposite direction).
`import {Test} from "forge-std/src/Test.sol";` (the iq-ai remapping convention).

## Test matrix (Cases A–E) → `AgentRouterSellRuntime.t.sol`
- **A** `tokenAgent == 0` → revert `AgentNotFound`.
- **B** bootstrap happy path → router pulls exactly `_amountIn` agent tokens; `bootstrapPool.sell` receives them;
  recipient gets `quote` currency; router holds 0 of both; seller surrendered exactly `_amountIn`.
- **C** `_minAmountOut > quote` → revert `InsufficientAmountOut`.
- **D** `recipient != seller` → recipient gets currency; seller surrenders agent tokens, gets no currency.
- **E** Fraxswap killed path (etched factory/pair) → `_amountIn` agent tokens routed to the pair, `quote` currency to
  the recipient, `_minAmountOut` enforced, router holds 0.

## Deps present?
forge-std ✓, OZ v5 ✓, dev-fraxswap ✓, solc 0.8.25 ✓, cancun ✓. → MODERATE confirmed; harness built and runs (see
`runtime_matrix.md` / `execution_output.txt`).
