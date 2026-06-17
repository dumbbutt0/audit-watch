# P122 — Minimal runtime question

> **Can a permissionless caller of `claim` (a) claim for a `minter_` they don't control / without a valid
> signature-or-merkle entitlement, (b) over-claim beyond the per-art guards, or (c) exploit the fee-binding gap —
> excess `msg.value` stuck, or underpayment subsidized by the contract's standing balance — to bypass the mint fee
> or drain held funds?**

One question. The harness answers it; source only frames it.

## YES (CONFIRMED high-impact) would require
An executed test where a caller mints for a minter without a valid signer signature / merkle proof, mints past
`maxSupply` / outside the window, or unconditionally drains arbitrary funds.

## NO (KILLED high-impact) requires
Executed tests showing the signature/merkle entitlement and the cap/window guards revert unauthorized attempts, with
no minter spoof and no over-claim.

## Secondary (fee-binding) — record the runtime behavior either way
- overpayment via `claim`: is the excess refunded or stuck?
- underpayment via `claim`: does it revert (empty balance) or succeed by drawing on the contract's standing balance?

## Scope
- The trusted `phiSignerAddress` (phi's backend signer) is taken as honest; "having a valid signature" = being an
  authorized minter, not an attacker capability.
- Severity is human-owned; this document assigns none.
