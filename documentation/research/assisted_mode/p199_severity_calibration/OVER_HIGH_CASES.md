# P199 — over-HIGH cases (Medium/Low awarded, rated ≥ HIGH)

8 confound-free over-HIGH cases (awarded Medium/Low, blind verdict ≥ HIGH), each cited to its artifact.

| # | corpus | surface | awarded | verdict | awarded ids | why it is Medium/Low in reality |
|---|---|---|---|---|---|---|
| 1 | quantamm | afterUpdate | Medium | HIGH | M-03, M-10, L-01 | unbounded-array gas-DoS / transfer-griefing / wrong-type — DoS+griefing, no theft |
| 2 | quantamm | UpdateWeightRunner._getData | Medium | HIGH | M-06 | unhandled oracle revert = **liveness/DoS**, not fund-loss (the exact P186/P187 M-06 case) |
| 3 | quantamm | MultiHopOracle._getData | Low | HIGH | L-02 | sequential-division **precision** loss — dust magnitude |
| 4 | ark | withdrawTokens | Medium | HIGH | AK-M2 | non-`onERC721Received` receiver → **stuck** NFT (recoverable/griefing), not theft |
| 5 | panoptic | _getRequiredCollateral… | Medium | HIGH | M-02 | credits-not-accumulated → **local** under-credit, conditional |
| 6 | panoptic | twapEMA | Medium | HIGH | M-03 | EMA destructure order — mispricing, bounded |
| 7 | centrifuge | IM-04 (processDeposit) | Medium | HIGH | M-04, M-05 | deposit-for-others **DoS** / Escrow-share **starvation** — griefing, no theft (M-04 also FM-2 wrapper/callee) |
| 8 | centrifuge | RM-12 (detectTransferRestriction) | Medium | HIGH | M-08 | restriction **compliance** gap (sender not checked) — regulatory, not fund-loss |

## Pattern
None of the 8 has a proven, permissionless, material **theft / insolvency / permanent-loss** path. They are:
**DoS/liveness** (2,4,7), **griefing** (1,7), **precision/dust** (3), **bounded local mispricing** (5,6), or
**compliance** (8). The blind stack recognised a *valid mechanism* and emitted the threat **ceiling** (HIGH) without
a step to demote to the *proven* impact tier (Medium/Low).

## Contrast: the 1 correctly-graded Medium
`centrifuge IM-06 → M-07` (rounding direction) — the only MEDIUM_THREAD verdict. The mechanism is intrinsically
bounded (per-tx rounding), so even the un-gated stack landed on Medium. This is the existence proof that a
bounded-magnitude mechanism *can* be graded Medium — the gate just needs to make that the rule, not the exception.
