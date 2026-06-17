# P120 — Minimal runtime question

> **Can a permissionless caller of `collectProtocolFees(pool)` redirect or extract protocol fees to an
> attacker-controlled address (theft), or break fee accounting — given the arbitrary `pool` argument and the
> `balanceOf(this)` notify amount?**

One question. The harness answers it; source only frames it.

## What a YES (CONFIRMED) would require
An executed test in which an arbitrary EOA caller ends up with a positive token balance it did not start with, or
fees are routed to a caller-controlled address instead of the legitimate `treasury` / voter-resolved `feeDist`.

## What a NO (KILLED) requires
Executed tests showing that across the reachable branches (live gauge, no gauge, attacker fake pool) the caller
receives nothing and every recipient is the hardcoded `treasury` / `address(this)` / voter-resolved `feeDist`.

## Scope
- Primary = theft / redirection (the high-value reading of a permissionless fee-collection function).
- Secondary observation = the `balanceOf(this)` cross-pool misattribution quirk (recorded, but it needs a donation
  = self-loss, so it is not attacker-profitable theft).
- The trusted `voter`'s gauge/feeDist resolution is taken as honest (governance-controlled), per the protocol model.
