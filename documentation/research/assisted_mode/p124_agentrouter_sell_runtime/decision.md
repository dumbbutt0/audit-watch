# P124 — Decision: AgentRouter.sell (NOVEL candidate)

## Terminal state: **KILLED_RUNTIME**

Runtime decided. The harness refuted the router-level attacker hypotheses with executed assertions on both code
paths — not source-only reasoning. Symmetric mirror of P123 (`buy`).

| KILLED condition (spec) | Evidence (runtime) |
|---|---|
| guards cannot be bypassed | Case A: selling a token with no agent reverts `AgentNotFound`; Case C: `_minAmountOut > amountOut` reverts `InsufficientAmountOut` (PASS). |
| caller surrenders the full amount; no free currency | Case B: the seller gives up **exactly `_amountIn`** agent tokens and `bootstrapPool.sell` receives that full amount; Case E: the full `_amountIn` is routed to the Fraxswap pair (PASS). |
| recipient gets the output; router retains nothing | Cases B/D/E: `_recipient` receives the currency output and the router holds **0 currency and 0 agent token** afterward — no skim, no retention, no over-issue (PASS). |

**Verdict:** the high-ranked, permissionless `AgentRouter.sell` is a thin, correct router on both branches — it
enforces agent-existence + slippage, pulls exactly `_amountIn` agent tokens, forwards them, delivers the currency
output to the recipient, and keeps nothing. A permissionless caller cannot obtain currency for free, bypass slippage,
drain the router, or sell a non-existent agent → **KILLED_RUNTIME**. With P123, this completes the AgentRouter
buy/sell pair at the router level — both clean runtime REFUTATIONs.

## Out-of-scope (recorded as NEEDS_CONTEXT, not settled here)
The economically interesting questions live in the COLLABORATORS, not the router, and are mocked here:
- `BootstrapPool` bonding-curve sell pricing / fee / `killed` transition.
- Fraxswap `getAmountOut` / `sync` (donation skim) / reserves / fee tier — the IQ-M-01 `moveLiquidity` area.
These require the real pool/Fraxswap math (heavier setup or a Fraxtal fork, cf. P104) and remain open (NEEDS_CONTEXT).

## Scope / honesty notes
- `_recipient` is arbitrary (sell-for-another), but the caller always surrenders the agent tokens — not a privilege.
- HARNESS_MODERATE; both branches covered (bootstrap directly, Fraxswap via `vm.etch` at the hardcoded factory).
- **No severity assigned**, no report, no submission package, no READY state, no production wiring (hard stops).

## Hard-stop self-check
- KILLED_RUNTIME claimed only with passing runtime tests (Cases A–E all PASS, executed). ✓
- No source-only reasoning used as runtime proof — guards / transfers / residual balances are executed assertions. ✓
- No severity / report / submission / READY token; no production wiring. ✓
- iq-ai `src/` **unmutated** — `AgentRouter.sol` (sha bb063429); the harness is a test-only file under
  `/tmp/p102-iqai/test/audit/`. ✓
