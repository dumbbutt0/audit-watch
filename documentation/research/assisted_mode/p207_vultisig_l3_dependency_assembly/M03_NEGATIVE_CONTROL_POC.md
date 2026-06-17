# P207 — M-03 negative control (DEMOTED, executed)

Harness: `pocs/p207/test/M03_capBypass.t.sol` (solc 0.7.6). Real `ILOPool` (cloned, byte-identical `realsrc/`) +
`ManagerStub`; no V3 pool needed (`buy()` never calls the live pool).

## Mechanism executed
`maxCapPerUser` is enforced per-NFT-position (`raiseAmount <= maxCapPerUser − _position.raiseAmount`). Since `buy()`
mints a fresh position when `balanceOf(recipient)==0`, an actor can: buy up to the cap → transfer the NFT to a fresh
account → buy again → a new position with `raiseAmount=0` allows another full-cap allocation.

## Executed result (`forge test`, pass)
- attacker buys `100e18` (cap) → position raiseAmount = `100e18`.
- further same-position buy `reverts("UC")` (cap holds for that position).
- attacker transfers the NFT to a mule (`balanceOf(attacker)==0`).
- attacker buys `100e18` again → fresh tokenId, raiseAmount = `100e18`.
- **L2:** attacker-controlled allocation = `200e18` > `maxCapPerUser = 100e18` → invariant bypassed.
- **L3:** attacker **paid full `raiseAmount` (100e18) for the extra allocation** (1:1), and pool custody =
  `200e18` = exactly what was paid in → **no protocol/victim value extracted**.

## L3 verdict
`MEDIUM_OR_LOWER` (DEMOTE) — a bounded invariant break with no realized material theft/loss (the bypasser pays fair
price). Matches the awarded **Medium**; the blind stack's HIGH (v-01) is over-rated. This demotes a **genuine awarded
finding** executably — the gap P205 left open (its executed negative control targeted a by-design, non-awarded
feature).
