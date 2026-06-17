# P124 — Minimal runtime question

> **Can a permissionless caller of `sell` obtain currency without surrendering the full `_amountIn` of agent tokens,
> bypass the `_minAmountOut` slippage guard, cause the router to retain/skim funds, or sell against a non-existent
> agent — i.e. is the ROUTER itself (as opposed to the delegated pool pricing) safe, on both the bootstrap and
> Fraxswap paths?**

One question. The harness answers it; source only frames it.

## YES (CONFIRMED) would require
An executed test where the caller receives currency while surrendering less than `_amountIn` of agent tokens, the
`_minAmountOut` guard fails to revert an under-output trade, the router keeps a residual balance an attacker can later
take, or a sell against `tokenAgent == 0` proceeds.

## NO (KILLED) requires
Executed tests showing `AgentNotFound` + `InsufficientAmountOut` revert appropriately, the caller surrenders exactly
`_amountIn` agent tokens, the recipient receives the pool/pair currency output, and the router holds zero of both
tokens afterward — on both the bootstrap and Fraxswap branches.

## Scope
- The **pricing** of `BootstrapPool.sell` (bonding curve) and Fraxswap (`getAmountOut`/`sync`/reserves) is **out of
  scope** for this router-level harness (mocked collaborators) → recorded as NEEDS_CONTEXT.
- Severity is human-owned; this document assigns none.
