# P125 — Minimal runtime question

> **Does `BootstrapPool` uphold its economic invariants under permissionless trading — constant-product `k`
> non-decreasing, no round-trip profit, solvency (never pays out currency it does not hold), reserve-neutral
> permissionless `sweepFees`, and donation-safety (a direct token transfer cannot make the donor net-profit or drain
> the pool) — or can a permissionless actor extract value from the delegated pricing engine?**

One question (a bundle of the deferred pricing invariants). The harness answers it with the REAL curve math; source
only frames it.

## CONFIRMED would require
An executed test where `k` decreases across a trade, a lone round-trip returns ≥ the input, the pool pays out more
currency than it holds, `sweepFees` shifts the reserves, or a donor ends net-positive — i.e. a permissionless actor
extracts value.

## KILLED requires
Executed tests showing all five invariants hold: round-trip strictly lossy, `k` non-decreasing, large sells revert
(solvent), `sweepFees` reserve-neutral + exact, and donation strictly unprofitable.

## Scope
- The harness uses the REAL pool/curve/fee/phantom math; only the standard ERC20 tokens are mocked (they are not the
  logic under test).
- Reserve carryover at `kill()` → `moveLiquidity` migration is OUT of scope (the awarded IQ-M-01 area) → NEEDS_CONTEXT.
- Severity is human-owned; this document assigns none.
