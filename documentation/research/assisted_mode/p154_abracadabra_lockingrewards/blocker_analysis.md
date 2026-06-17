# P154 — Blocker / Residual Analysis

This candidate is **not blocked** — it converted to `reportable_candidate_needs_human_review`. This file
records the single residual question the human reviewer must resolve, so the routing is honest and the
reviewer's job is scoped.

## The one residual: severity grade + trust-model scope (NOT validity)
What is **already proven** (not for the reviewer to re-litigate): the mechanism (post-expiry boost
retention), the unprivileged reachability, and the zero-sum impact (A's gain = B's loss). The reviewer is
**not** asked "is this real?" — it is.

The reviewer **is** asked: *given the program's trust model for the `onlyOperators` role, what severity does
the operator-cadence-dependent magnitude warrant, and is operator-delay in scope?*

### Inputs for that decision
- **Lower-bound case:** operator calls `processExpiredLocks` exactly at `unlockTime` → over-accrual ≈ 0.
- **Typical case:** NatSpec cadence "once a `rewardDuration`" → up to ~1 epoch of boosted-after-expiry
  accrual per affected lock.
- **Upper-bound case:** operator negligent/absent → unbounded; the locker keeps the full boost share
  indefinitely, and **no on-chain mechanism** (user or otherwise) stops it.
- **Aggravators:** the user cannot self-remediate (no user unlock path); the loss falls on innocent
  third-party stakers, not on the operator; the boost multiplier can be up to design max (3× in this test,
  configurable higher).
- **Mitigators:** `onlyOperators` is a semi-trusted role; the protocol clearly *intends* prompt processing;
  many programs treat "trusted role must run routine maintenance" as Low/informational or out-of-scope.

### Suggested resolution path for the human
1. Confirm the program's scope statement on trusted-operator timeliness.
2. If operator delay is in scope → grade Medium (typical) / High (if a keeper is not guaranteed and the
   boost/locked TVL is large). If out of scope → downgrade to Low/informational and record as
   `severity_too_low`.
3. Independently run a KB/duplicate check to set `novelty_clear` (currently `unknown`).

## Pre-registered counterfactuals (already ruled out by evidence)
| If… | …outcome would have been |
|---|---|
| de-boost automatic at `unlockTime` | runtime_refuted |
| user-callable unlock existed | severity_too_low |
| NatSpec framed persistent boost as intended | needs_context / intent_ambiguous |
| corrected reference showed zero delta | runtime_refuted |

None hold → the honest terminal outcome is `reportable_candidate_needs_human_review`,
`submission_ready=false`.
