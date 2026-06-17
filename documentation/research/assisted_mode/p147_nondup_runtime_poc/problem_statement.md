# P147 — Problem Statement

P143/P145 runtime-confirmed B1 (noya) and B5 (blackhole); P146 surfaced them in the runtime panel. Both are
`duplicate_known` (awarded eval bugs). **P147 takes the runtime-PoC method to a target with no local answer key**,
so the result is **non-duplicate locally** (`duplicate_status=duplicate_unknown`) — producing a `runtime_confirmed`
panel row WITHOUT `duplicate_known`, while keeping the P138 prompt scorecard baseline byte-for-byte unchanged.

## Primary question
Can the value-provenance / recipient-provenance method find a value-or-recipient divergence in a holdout (no local
answer key) and **runtime-confirm** it as a non-duplicate panel row — or honestly kill it?

## Target & answer
**`centrifuge-2023-09-holdout` `UserEscrow.transferOut`** (no local answer key → `duplicate_unknown`). The escrow
holds funds *for* a `destination` (`destinations[token][destination]`), but `transferOut(token, destination,
receiver, amount)` pays a **different** `receiver` when `receiver == destination || allowance(destination,
receiver) == type(uint256).max`, and **never reduces that allowance**. So funds escrowed for `destination` can be
redirected to an unrelated `receiver` whose only link is a stale/unrelated infinite ERC20 allowance.

**RUNTIME_CONFIRMED_NONDUP.** The real `UserEscrow`, deployed locally, paid `destination`'s 1000e18 escrow to an
unrelated `receiver` (0xBEEF); a corrected reference (`receiver == destination`) reverts; a control
(`receiver == destination`) matches; and a repeat shows the allowance is never reduced. The panel now shows this
as a `runtime_confirmed` / `duplicate_unknown` / `runtime_only` row — the first runtime-confirmed row that is not
`duplicate_known` — with the 11-item prompt baseline untouched.

## Honesty boundaries
- Holdouts have **no answer key**, so the direct value-provenance review is not answer-key-contaminated.
- The divergence is **source-verified** and **runtime-confirmed**, but it is **intent-dependent**: the NatSpec
  frames the allowance check as "additional protection." So runtime confirmation proves the *mechanism*; **severity
  / validity is for human review** (`requires_human_review=true`, `requires_poc_review=true`, `submission_ready=
  false`). `duplicate_status=duplicate_unknown` — not claimed novel or awarded.
- Two earlier candidates were honestly rejected as **design-intended controls**, not bugs: loopfi
  `claimFromConverter` (pays the converter by NatSpec) and loopfi `getReward`/`_getReward` (pays the caller) — no
  divergence.
