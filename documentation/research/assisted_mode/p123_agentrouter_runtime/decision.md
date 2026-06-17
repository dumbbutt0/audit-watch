# P123 — Decision: AgentRouter.buy (NOVEL candidate)

## Terminal state: **KILLED_RUNTIME**

Runtime decided. The harness refuted the router-level attacker hypotheses with executed assertions on both code
paths — not source-only reasoning.

| KILLED condition (spec) | Evidence (runtime) |
|---|---|
| guards cannot be bypassed | Case A: buying a token with no agent reverts `AgentNotFound`; Case C: `_minAmountOut > amountOut` reverts `InsufficientAmountOut` (PASS). |
| caller pays the full amount; no free tokens | Case B: the buyer pays **exactly `_amountIn`** and `bootstrapPool.buy` receives that full amount; Case E: the full `_amountIn` is routed to the Fraxswap pair (PASS). |
| recipient gets the output; router retains nothing | Cases B/D/E: `_recipient` receives the pool/pair output and the router holds **0 currency and 0 agent token** afterward — no skim, no retention, no over-issue (PASS). |

**Verdict:** the high-ranked, permissionless `AgentRouter.buy` is a thin, correct router on both branches — it
enforces agent-existence + slippage, pulls exactly `_amountIn`, forwards it, delivers the output to the recipient, and
keeps nothing. A permissionless caller cannot obtain tokens for free, bypass slippage, drain the router, or buy a
non-existent agent → **KILLED_RUNTIME**. A clean runtime REFUTATION of a NOVEL candidate (the methodology that
CONFIRMED P117 and KILLED P118/P120/P121/P122 also KILLS this).

## Out-of-scope (recorded as NEEDS_CONTEXT, not settled here)
The economically interesting questions live in the COLLABORATORS, not the router, and are mocked here:
- `BootstrapPool` bonding-curve pricing / fee / `killed` transition.
- Fraxswap `getAmountOut` / `sync` (donation skim) / reserve manipulation / fee tier — the area of the awarded
  IQ-M-01 `moveLiquidity` pair-adoption finding.
These require the real pool/Fraxswap math (heavier setup or a Fraxtal fork, cf. P104) and remain open (NEEDS_CONTEXT);
they are not promoted.

## Scope / honesty notes
- `_recipient` is arbitrary (buy-for-another), but the caller always pays — not a privilege.
- HARNESS_MODERATE; both branches covered (bootstrap directly, Fraxswap via `vm.etch` at the hardcoded factory).
- **No severity assigned**, no report, no submission package, no READY state, no production wiring (hard stops).

## Hard-stop self-check
- KILLED_RUNTIME claimed only with passing runtime tests (Cases A–E all PASS, executed). ✓
- No source-only reasoning used as runtime proof — guards / transfers / residual balances are executed assertions. ✓
- No severity / report / submission / READY token; no production wiring. ✓
- iq-ai `src/` **unmutated** — `AgentRouter.sol` (sha bb063429); the harness is a test-only file under
  `/tmp/p102-iqai/test/audit/`. ✓
