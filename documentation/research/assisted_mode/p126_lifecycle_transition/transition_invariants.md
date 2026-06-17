# P126 — Transition invariants (kill() → moveLiquidity())

Explicit, executable invariants for the lifecycle transition. Each maps to runtime scenarios (see `runtime_matrix.md`).
Verdict is from executed evidence only; no severity/exploitability is claimed.

| # | Invariant | Statement | Scenarios | Result |
|---|---|---|---|---|
| **I1** | value conservation | `poolCurrency(pre-kill) == pairCurrency + feeTo.currencyFee`; `poolAgent(pre-kill) == pairAgent + agentLeftover + feeTo.agentFee`; LM retains ~0. | A, B | HOLDS |
| **I2** | fee accounting conserved | swept fees == accrued `currencyTokenFeeEarned`/`agentTokenFeeEarned`; fees go to the AgentFactory (feeTo), never into the migrated liquidity, no double-count. | A, B | HOLDS |
| **I3** | donations not donor-extractable | a pre-kill donation (currency or agent) flows into the pair + agent; the donor recoups nothing. | C, D | HOLDS |
| **I4** | migration output integrity | the pair is seeded at the pool spot price (`pairCurrency/pairAgent ≈ price`) with the LM's real holdings; LP routed per `shareToBamm`/agent; stage advanced. | A | HOLDS |
| **I5** | no attacker profit from boundary manipulation | manipulating the pre-kill spot price then arbing the freshly-seeded pair does not net the attacker value vs the manipulation cost. | E | HOLDS (net **loss**) |
| **I6a** | availability (no block/DoS) | migration cannot be blocked/reverted by attacker-prepared reserve state (e.g. agent donation inflating `liquidityAmount`). | D | HOLDS (completes) |
| **I6b** | control (no forced-early) | migration cannot be forced *materially earlier than intended* via attacker-controlled state. | F | **PARTIAL — see note** |

## I6b note (the one non-clean result — a runtime CONTROL fact, not an extraction)
Scenario F shows that an attacker **can** force migration before any organic bootstrap by donating exactly the gate
amount (`targetCCYLiquidity`) of currency and immediately calling the permissionless `moveLiquidity()`. The migration
fires (`setAgentStage→1`) when it otherwise reverts (`"Bootstrap end-criterion not reached"`).

This is a **timing/control** primitive, NOT a value extraction:
- the attacker **pays the full gate threshold** as a non-recoverable donation (recouped **0**),
- the donation becomes migrated liquidity owned by the **agent** (not the attacker),
- it is functionally equivalent to **"anyone may complete the bootstrap by funding it to the target."**

Whether "completion-by-self-funding" is *materially earlier than intended* is **intent-dependent** (the gate's
end-criterion is met either way) and is a human/protocol-design judgement. Per the hard stops, **no severity or
exploitability is claimed**; this is recorded as an executed control fact and attributed to the interaction boundary
(permissionless `moveLiquidity` + a donation-inflatable gate).

## Out of scope
The awarded pair-adoption M-01 (the "pair already exists" branch of `addLiquidityToFraxswap`) is **not** retested here;
P126 exercises the clean `createPair` branch only.
