# P209 — L3 readiness state machine

## States
| state | meaning |
|---|---|
| `THREAT_CEILING_HIGH` | deep-trace verdict High/Critical (ceiling only) |
| `MECHANISM_CONFIRMED` | passed min_confirm_gate + confirm_gate (field presence + reachability credible) |
| `NEEDS_L3_HARNESS` | High target, mechanism confirmed, but no L3 PASS yet (l3_status NOT_ATTEMPTED/NEEDS_HARNESS) |
| `L3_PASS` | executed L3 PoC shows material realized impact (high_promotion_allowed=true) |
| `L3_FAIL_MEDIUM` | L3 ran, no material High impact → calibrated Medium |
| `L3_INCONCLUSIVE` | L3 could not reach the path (dependency/setup); severity undecided, not High-ready |
| `HUMAN_OVERRIDE_HIGH` | human-certified L3-equivalent with written rationale (conditions 2–7 still met) |
| `HIGH_SUBMISSION_READY` | High package readiness granted (requires L3_PASS or HUMAN_OVERRIDE_HIGH) |
| `MEDIUM_SUBMISSION_READY` | Medium package readiness (source-proven mechanism + impact; no L3 required) |
| `BLOCKED_BY_MISSING_L3` | High target without L3 PASS/override → `blocked_by_missing_l3_poc` |
| `BLOCKED_BY_INSUFFICIENT_IMPACT` | impact not material enough for High (and not a valid Medium) |
| `BLOCKED_BY_SOURCE_REFUTATION` | source refutes the mechanism → invalid |

## Allowed transitions
```
THREAT_CEILING_HIGH -> MECHANISM_CONFIRMED            (min_confirm + confirm_gate pass)
MECHANISM_CONFIRMED -> NEEDS_L3_HARNESS               (High target, no L3 yet)
MECHANISM_CONFIRMED -> MEDIUM_SUBMISSION_READY        (Medium target, source-proven impact)
NEEDS_L3_HARNESS    -> L3_PASS | L3_FAIL_MEDIUM | L3_INCONCLUSIVE | HUMAN_OVERRIDE_HIGH
L3_PASS             -> HIGH_SUBMISSION_READY
HUMAN_OVERRIDE_HIGH -> HIGH_SUBMISSION_READY
L3_FAIL_MEDIUM      -> MEDIUM_SUBMISSION_READY | BLOCKED_BY_INSUFFICIENT_IMPACT
L3_INCONCLUSIVE     -> NEEDS_L3_HARNESS               (retry/author harness) 
NEEDS_L3_HARNESS    -> BLOCKED_BY_MISSING_L3          (High target, readiness attempted without L3)
any (source-refuted)-> BLOCKED_BY_SOURCE_REFUTATION
```
Re-entry: `BLOCKED_BY_MISSING_L3 -> L3_PASS/HUMAN_OVERRIDE_HIGH -> HIGH_SUBMISSION_READY` once evidence is supplied.

## Forbidden transitions (hard invariants)
- `THREAT_CEILING_HIGH -> HIGH_SUBMISSION_READY` without `L3_PASS` or `HUMAN_OVERRIDE_HIGH`. ❌
- `NEEDS_L3_HARNESS -> HIGH_SUBMISSION_READY`. ❌
- `BLOCKED_BY_SOURCE_REFUTATION -> *_SUBMISSION_READY` (any submission_ready). ❌
- `L3_FAIL_MEDIUM -> HIGH_SUBMISSION_READY`. ❌

Also forbidden by construction: any transition that flips canonical `submission_ready`/`routing_allowed` (the overlay
never does), and any path that reaches a *_SUBMISSION_READY state while bypassing `MECHANISM_CONFIRMED`.

## Notes
- Default for a candidate with no L3 record + High target = `NEEDS_L3_HARNESS` (fail-closed for High).
- Medium targets never require passing through L3 states.
