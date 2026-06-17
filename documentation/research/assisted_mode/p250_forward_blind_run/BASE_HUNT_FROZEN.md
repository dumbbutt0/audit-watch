# P250 — Base Hunt (blind, NO checkpoint) — FROZEN pre-reveal

Genuine read of the in-scope source (PrincipalToken 74-item core, PrincipalTokenUtil, RayMath, YieldToken;
proxy/beacon contracts are standard OZ). P245 gate: all critical items READ_FULL → coverage complete, gate
PASS. No checkpoint used. Candidates are the system's base output BEFORE the accounting checkpoint.

## Base candidates
| id | sev | locus | mechanism |
|---|---|---|---|
| B-1 | Medium | PrincipalToken._convertIBTsToSharesPreview vs _depositIBT | `previewDeposit` path rounds shares UP (`_getPTandIBTRates(true)` → PT rate floored → shares ceil) while actual `_depositIBT` rounds shares DOWN (`Rounding.Floor`); ERC5095 preview should be ≤ actual → preview overstates shares a depositor receives (integrator/slippage mismatch). |
| B-2 | Medium | PrincipalToken.storeRatesAtExpiry | permissionless + snapshots ptRate/ibtRate at the FIRST post-expiry call's block; front-runnable to a favorable IBT-rate block → affects all post-expiry redemptions. |
| B-3 | Low/Med | PrincipalToken.flashLoan | not `nonReentrant`; lends the ENTIRE IBT balance (incl. user-backing IBT); callback can reenter non-guarded claim/redeem-view paths. |
| B-4 | Low | PrincipalToken.updateYield / storeRatesAtExpiry | public checkpoints callable for any user (griefing/timing; mostly benign). |
| B-5 | Medium | PrincipalTokenUtil._computeYield | negative-yield/PT-depeg branch mixes Floor/Ceil + a SAFETY_BOUND dust cutoff; complex Ray math with potential yield over/under-attribution on depeg (suspected, not fully pinned). |

## Coverage / proof
P245 gate: 104/104 critical READ_FULL → PASS. Proof conversion: BLOCKED_BY_BUILD (no vendored deps).

## Note on base strength
This base hunt already surfaced the principal accounting issue (B-1 rounding direction) and a depeg-math
suspicion (B-5) — because the contest is small and was read carefully. The checkpoint's marginal contribution
(next doc) is measured AGAINST this base, not against a strawman.

FREEZE: base candidates above are final pre-reveal.
