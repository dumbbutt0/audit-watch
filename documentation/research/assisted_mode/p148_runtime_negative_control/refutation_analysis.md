# P148 — Refutation Analysis

## Which axis was refuted: **recipient-divergence**

The B5 suspicion requires a code path where `claim_many` resolves a reward **recipient** differently from `claim`
(blackhole: `claim_many` omits the AVM `getOriginalOwner` correction and pays `ownerOf`). The refutation shows
velodrome has **no recipient-resolution path at all**:

| check | result |
|---|---|
| Does `claim` resolve an external recipient? | No — only `deposit_for(_tokenId, amount)` |
| Does `claim_many` resolve an external recipient? | No — only `deposit_for(_tokenId, amount)` |
| Any `ownerOf` / AVM / expired-lock transfer branch? | None in the contract |
| Runtime: external recipient (0xBEEF) paid? | 0 in both paths |
| Runtime: do the siblings differ? | No — both `deposit_for` their own tokenId, equal amount |

⇒ The invariant "reward is credited to the claimed tokenId via `deposit_for`, never transferred to a resolved
external recipient" **always holds** in both siblings. The suspected divergence is impossible. **RUNTIME_REFUTED.**

## Why not the other negative labels
- Not **runtime_partial**: a nonzero `_claim` was driven and both siblings executed fully; the routing was
  observed end-to-end, not merely shape-inspected.
- Not **runtime_blocked**: the contract compiled and the path executed with mocks only; no missing dependency.
- Not **runtime_confirmed**: there is no divergence/state-delta to confirm (forbidden this phase anyway).

## Calibration value
This proves the runtime process can produce a clean **negative** result with evidence — distinguishing
"same family, real bug" (blackhole B5, `runtime_confirmed`) from "same family, no such bug" (velodrome,
`runtime_refuted`) — so the dashboard's `runtime_confirmed` rows carry meaning (they are not the only thing the
process can output). No "almost-bug" ambiguity: the refuted row is explicitly killed, `routing_allowed=false`,
`submission_ready=false`, and excluded from the prompt baseline.
