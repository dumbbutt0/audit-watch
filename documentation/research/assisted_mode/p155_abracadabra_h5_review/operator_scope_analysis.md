# P155 — Gate 3: Operator / Trusted-Role Scope

| Question | Answer |
|---|---|
| Is `processExpiredLocks` permissioned? | **Yes** — `onlyOperators` (:397). |
| Who can call it? | The owner or any address the owner has `setOperator(_, true)` (OperatableV2). Not users. |
| Is the operator expected to maintain reward correctness? | **Yes** — de-boosting expired locks (which keeps reward shares correct) is *only* possible through this operator function; NatSpec documents the cadence ("once a `rewardDuration`", :395-396). |
| Does failure to process create user loss or only delayed accounting? | **Real user loss.** Rewards mis-allocated during an unprocessed window are finalized when claimed/vested (`_getRewards`, :597-657); later processing fixes only *future* windows, not the already-accrued/claimed ones. So it is not merely delayed accounting. |
| Does the protocol rely on trusted maintenance? | **Yes** — reward-share correctness depends on the operator running `processExpiredLocks` promptly. |
| Is this a keeper/operator-liveness issue? | **Partly.** It has the shape of a keeper-liveness issue, but with the aggravator that the loss falls on *third-party honest stakers* who cannot self-protect (no user de-boost). |
| Does trusted-operator liveness reduce severity or make it out-of-scope? | **Reduces (bounds) severity.** With the documented cadence the per-lock window is small; magnitude grows only with operator negligence. Whether a *fully*-trusted-operator reading places it out of scope is a program-specific call not determinable locally. |

## Classification: **trusted_operator_liveness_bounds_severity**
Not `trusted_operator_requirement_blocks_reportability` — honest third parties bear real, non-self-correcting
loss, so the trusted role does not fully neutralize it. Not `trusted_operator_only_design` — the loss is real,
not a benign design choice. Not `not_operator_dependent` — magnitude is clearly a function of operator delay.
The trusted-operator-liveness assumption **bounds** the severity (caps the typical window, no protocol-fund
loss) without removing the candidate; the final out-of-scope determination is deferred to the human with the
program's trust model in hand.
