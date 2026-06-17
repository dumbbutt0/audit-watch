# Minimal reproduction hypothesis

Candidate: `wildcat-2024-08 :: WildcatMarket.closeMarket`.

## Source-backed hypothesis attempt

Read WildcatMarket.closeMarket. It is `onlyBorrower nonReentrant sphereXGuardExternal` — a PRIVILEGED borrower-only function, NOT a permissionless attacker path. (Note: the recommended ranking marked it permissionless because the body-only actor_clarity heuristic misses the `onlyBorrower` MODIFIER, which is in the signature, not the body — a ranking-precision gap.) Its closed-market accounting feeds the state that the awarded P95 H-01 exploited, but that bug lives in the sibling permissionless `executeWithdrawal`, not here. I could not form a source-provable exploit on closeMarket (privileged caller) and could not prove it safe (complex closed-market settlement); resolving it needs the cross-function/runtime path. Truthful terminal: NEEDS_CONTEXT.

## What runtime evidence would be required

A falsifiable runtime check could not be specified from source alone for this candidate (see rationale). Resolving it would require execution-backed evidence — e.g. a fork/local deployment plus a differential or invariant test across the cross-contract boundary named above — not further source reasoning. Absent that, the truthful terminal is `NEEDS_CONTEXT`; no exploit is claimed and no finding is promoted.
