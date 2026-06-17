# P285 — LIMITATIONS

1. **Guard detection is bounded/static.** Gates recognized: `require`/`assert` args, `if (…)` with a `revert`/`return`
   in the same statement or braced block, `onlyX` modifiers, custom-error reverts. A guard that lives entirely inside an
   internal helper called in a gating position (a bare `_checkOwner();` statement, not inside require/if-revert) is
   classified UNKNOWN_READ → the candidate is held (NEEDS_GUARD_CONTEXT / value/state block), never falsely lifted.
2. **ERC4626 withdraw-on-behalf** (`if (msg.sender != owner) { _spendAllowance(...) }`) is UNKNOWN_READ — the allowance
   helper gates internally but no revert is visible in the span. Conservative (held, not READY); a real allowance bug
   would need the P284 conservation lens to lift.
3. **`whenNotPaused` / pause modifiers are treated as LIVENESS, not access guards** — they do not restrict who calls, so
   they no longer refute the attacker path. A pause-griefing/DoS concern would need a separate liveness lens.
4. **RECIPIENT vs VALUE read is heuristic** (LHS/arg name vocabulary). Both are non-guard, so the distinction never
   affects lift safety — only the descriptive label.
5. **Supervised eval, not blind, not production.** 12 eval audits; award titles/bodies never read by code. No production
   authority; advisory/eval-only; default-off; un-wired. Only the L2Governor regression PoC was run; the claim_many lift
   ships as a PoC-INTENT record (`outputs/claim_many_poc_intent.json`), not a full PoC.
6. **NEEDS_GUARD_CONTEXT did not trigger in this corpus** (the ambiguous-auth candidates were value/state classes caught
   by their own blocks first); it is exercised by a unit test and is a fail-safe for ACCESS-class ambiguity.
