# P156 — Gate 2: Operator-Scope Confirmation

## New decisive external fact
The contest materials state: **"Locks are released by a Gelato task offchain."** So `processExpiredLocks`
(the sole de-boost path, `onlyOperators` :397) is driven by an **automated keeper (Gelato)**, not ad-hoc
manual ops. This was not visible from source alone and materially refines P155's scope analysis.

| Question | Answer |
|---|---|
| Who controls processing? | An automated **Gelato keeper** task (operator), not users. |
| NatSpec cadence | "Should be called once a `rewardDuration`" (:395-396) — i.e., the keeper runs ~each epoch. |
| Can users self-remediate? | **No** — no user-callable unlock/de-boost. |
| Are rewards permanently misallocated once claimed? | **Yes** — `_getRewards` finalizes; later processing fixes only future windows. |
| Is operator delay a *normal* expected condition? | **No** — with an automated keeper, delay is an **exception** (keeper failure/lag), not normal operation. |
| Does the protocol promise fairness exactly at `unlockTime`? | Not explicitly; it relies on the keeper de-boosting "once a rewardDuration." |
| Does the inherited Convex/Curve lazy-expiry design change reportability? | It frames the lazy-expiry as **intended design** (public pattern), reducing novelty/severity weight, but does not eliminate the honest-staker loss during keeper downtime. |

## Reasoning
The automated keeper makes the over-accrual window **unlikely and short in normal operation** — it
materializes only when the Gelato task fails or lags. That is a classic **keeper/liveness** dependency,
which **bounds** severity. However, two facts keep it from being a pure design pass / fully out-of-scope:
(1) honest third-party stakers bear the loss and **cannot self-protect**; (2) the loss for elapsed windows
is **permanent** (not retroactively corrected). So the trusted/automated-operator assumption *bounds* but
does not *neutralize* the issue.

## Classification: **operator_liveness_bounds_severity_but_does_not_block**
Not `operator_liveness_blocks_reportability` (real, permanent, un-self-remediable third-party loss). Not
`accepted_lazy_expiry_design` (the loss is a real consequence, not a documented-accepted behavior). Not pure
`keeper_issue_low_or_QA` (there is a concrete unprivileged loss path, though it leans low). The automated
keeper bounds severity toward Low; sustained keeper failure raises it to Medium.

**operator_scope_status = operator_liveness_bounds_severity_but_does_not_block**
