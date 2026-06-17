# Scope Decision Memo

**This memo presents both readings and decides neither. The in/out-of-scope call is the program's.**

## Reading A — in-scope (valid Low)
A real, unprivileged, runtime-confirmed **user-to-user reward misallocation**: an expired boosted lock keeps
its multiplier in reward accounting until an operator processes it, so honest stakers are diluted during the
post-expiry/pre-sweep window. Honest third parties bear the loss and **cannot self-remediate** (no
user-callable de-boost). Under this reading it is a valid **Low** (Medium if sustained keeper delay counts).

## Reading B — downgrade / out-of-scope
If the program treats the `onlyOperators` keeper as **fully trusted** and routine `processExpiredLocks`
maintenance as an **assumed invariant**, then the residual window is an accepted operational characteristic,
and the issue may be judged **Low/QA or out-of-scope** (a keeper-liveness/maintenance assumption rather than
a contract defect).

## What tips the decision (for the human, with the program's rules)
- Does the program's scope/known-issues doc treat keeper/operator timeliness as a trusted assumption?
- Does it accept "honest third parties lose value during normal operator cadence" as reportable?
- Is the inherited Convex/Curve lazy-expiry design called out as accepted?

## Boundary statement
The package's recommendation (severity_memo.md) is **Low baseline**; the scope verdict (in-scope-Low vs
out-of-scope-QA) is **deferred to the program/human** and is **not** decided here.
