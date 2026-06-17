# P124 — Runtime matrix

Command: `forge test --match-contract AgentRouterSellRuntime --evm-version cancun -vvv`
Project: `/tmp/p102-iqai` (iq-ai repo; `src/` unmutated; test-only file under `test/audit/`; on-disk `node_modules`).
Amounts: `_amountIn = 100e18` agent token; bootstrap quote = `90e18` currency; Fraxswap quote = `80e18` currency.

| Case | Scenario (caller = permissionless seller) | Result | Evidence |
|---|---|---|---|
| **A** | `sell` for a token with `tokenAgent == 0` | **PASS** | reverts `AgentNotFound` |
| **B** | bootstrap path (`killed==false`), exact approval | **PASS** | `out == 90e18`; seller surrendered exactly `100e18` agent; `bootstrapPool.lastAmountIn == 100e18`; recipient got `90e18` currency; **router holds 0 currency & 0 agent** |
| **C** | `_minAmountOut = 91e18 > quote 90e18` | **PASS** | reverts `InsufficientAmountOut` |
| **D** | `recipient != seller` | **PASS** | recipient got `90e18` currency; seller got 0 currency, surrendered `100e18` agent |
| **E** | Fraxswap path (`killed==true`, factory etched at `0xE305…`) | **PASS** | `out == 80e18`; `_amountIn` agent routed to the pair (`pair.agent == 100e18`); recipient got `80e18` currency; router holds 0 agent |

All 5 tests pass (executed). Full log: `execution_output.txt`.

## Reading
- **A / C** the router-level guards hold: non-existent agents and under-output trades revert.
- **B / D / E** the router pulls exactly `_amountIn` agent tokens, forwards them to the pool/pair, delivers the
  currency output to `_recipient`, and retains **nothing** on either branch. No skim, over-issue, or fund retention at
  the router level; `_minAmountOut` is the user's slippage protection.
- **Out of scope (NEEDS_CONTEXT):** the *pricing* returned by `BootstrapPool.sell` (bonding curve) and the Fraxswap
  pair (`getAmountOut`/`sync`/reserves) — settled by mocks here, not by real pool math.
