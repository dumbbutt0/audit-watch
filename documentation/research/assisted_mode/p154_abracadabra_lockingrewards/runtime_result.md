# P154 — Runtime Result

`forge test -vv` — 4/4 passed. Reward `earned()` per user (wei), 3× boost, R=700e18/epoch:

| Window | A (locker) | B (unlocked) | A:B | reading |
|---|---|---|---|---|
| W1 — lock **active** (control) | 524.999…e18 | 174.999…e18 | ~3:1 | **intended boost** — A committed |
| W2 — expired, **unprocessed** (mechanism) | +524.999…e18 | +174.999…e18 | ~3:1 | **BUG** — boost persists after expiry |
| W2 — expired, **processed** (corrected, real code) | +349.999…e18 | +349.999…e18 | ~1:1 | **fair** — prompt processing removes it |

## Quantified over-accrual (window 2, same T0)
- A unprocessed = 524.999…e18 · A processed = 349.999…e18 → **A over-accrual = 174.999…e18**
- B unprocessed = 174.999…e18 · B processed = 349.999…e18 → **B loss = 174.999…e18**
- **A's over-accrual == B's loss (zero-sum)** — asserted `assertApproxEqRel(overA, lossB, 1e12)`.

(The `.999…` are reward-rate integer-division dust; ratios are exact to 1e-6.)

## Interpretation
- **Mechanism CONFIRMED at runtime.** The real contract keeps `balanceOf(A)=3X` after `unlockTime`
  (`locked(A)` still `X`), so A keeps earning the 3× share. The corrected reference (prompt
  `processExpiredLocks`, real code) drives `balanceOf(A)=X` and the over-accrual to zero — isolating the
  single variable (processing timing). The control (active-lock window) confirms the boost is *intended*
  while committed, so the finding is specifically the **post-expiry** retention, not the boost itself.
- **Reachability CONFIRMED.** A is an ordinary EOA with no privileged setup; A cannot self-remediate
  (no user unlock), so the incorrect distribution is structural.
- **Impact CONCRETE and zero-sum.** Every wei A over-accrues is taken from honest staker B.

## Severity caveat (drives the human-review routing)
The over-accrual magnitude is a function of operator delay: ~0 if `processExpiredLocks` is called exactly at
`unlockTime`, growing each epoch the operator is late, and unbounded if it is never called. The NatSpec
*expects* (but does not enforce) processing "once a `rewardDuration`." Whether reliance on operator cadence
for reward-distribution correctness is an accepted trust assumption or a reportable defect — and the final
severity grade — is a human/scope judgment (see blocker_analysis.md), which is exactly why this is routed as
`reportable_candidate_needs_human_review` rather than auto-promoted.
