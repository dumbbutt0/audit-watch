# P123 — Minimal runtime question

> **Can a permissionless caller of `buy` obtain agent tokens without paying the full `_amountIn`, bypass the
> `_minAmountOut` slippage guard, cause the router to retain/skim funds, or buy against a non-existent agent — i.e.
> is the ROUTER itself (as opposed to the delegated pool pricing) safe, on both the bootstrap and Fraxswap paths?**

One question. The harness answers it; source only frames it.

## YES (CONFIRMED) would require
An executed test where the caller receives agent tokens while paying less than `_amountIn`, the `_minAmountOut` guard
fails to revert an under-output trade, the router keeps a residual balance an attacker can later take, or a buy
against `tokenAgent == 0` proceeds.

## NO (KILLED) requires
Executed tests showing `AgentNotFound` + `InsufficientAmountOut` revert appropriately, the caller pays exactly
`_amountIn`, the recipient receives the pool/pair output, and the router holds zero of both tokens afterward — on
both the bootstrap and Fraxswap branches.

## Scope
- The **pricing** of `BootstrapPool` (bonding curve) and Fraxswap (`getAmountOut`/`sync`/reserves) is **out of
  scope** for this router-level harness (mocked collaborators) → recorded as NEEDS_CONTEXT.
- Severity is human-owned; this document assigns none.
