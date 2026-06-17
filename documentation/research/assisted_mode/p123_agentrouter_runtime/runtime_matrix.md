# P123 — Runtime matrix

Command: `forge test --match-contract AgentRouterBuyRuntime --evm-version cancun -vvv`
Project: `/tmp/p102-iqai` (iq-ai repo; `src/` unmutated; test-only file under `test/audit/`; on-disk `node_modules`).
Amounts: `_amountIn = 100e18` currency; bootstrap quote = `90e18` agent; Fraxswap quote = `80e18` agent.

| Case | Scenario (caller = permissionless buyer) | Result | Evidence |
|---|---|---|---|
| **A** | `buy` for a token with `tokenAgent == 0` | **PASS** | reverts `AgentNotFound` |
| **B** | bootstrap path (`killed==false`), exact approval | **PASS** | `out == 90e18`; buyer paid exactly `100e18`; `bootstrapPool.lastAmountIn == 100e18`; recipient got `90e18`; **router holds 0 currency & 0 agent** |
| **C** | `_minAmountOut = 91e18 > quote 90e18` | **PASS** | reverts `InsufficientAmountOut` |
| **D** | `recipient != buyer` | **PASS** | recipient got `90e18`; buyer got 0 and paid `100e18` |
| **E** | Fraxswap path (`killed==true`, factory etched at `0xE305…`) | **PASS** | `out == 80e18`; `_amountIn` routed to the pair (`pair.currency == 100e18`); recipient got `80e18`; router holds 0 currency |

All 5 tests pass (executed). Full log: `execution_output.txt`.

## Reading
- **A / C** the router-level guards hold: non-existent agents and under-output trades revert.
- **B / D / E** the router pulls exactly `_amountIn`, forwards it to the pool (bootstrap) or pair (Fraxswap), delivers
  the output to `_recipient`, and retains **nothing** of either token on either branch. No skim, no over-issue, no
  fund retention at the router level; `_minAmountOut` is the user's slippage protection.
- **Out of scope (NEEDS_CONTEXT):** the *pricing* returned by `BootstrapPool.buy` (bonding curve) and the Fraxswap
  pair (`getAmountOut`/`sync`/reserves) — settled by mocks here, not by real pool math.
