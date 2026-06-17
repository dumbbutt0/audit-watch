# Severity Memo

**Recommendation: Low baseline · Medium conditional. Not High. Not invalid.**

## Ladder
- **Low (baseline) — recommended.** Under the stated keeper cadence (`processExpiredLocks` "should be called
  once a `rewardDuration`") the post-expiry/pre-sweep window is **bounded and ordinary**, the per-gap
  misallocation is **small**, the effect is **zero-sum among stakers**, and there is **no protocol-fund loss**.
- **Medium (conditional).** If the program treats **sustained keeper failure / delayed operator processing**
  as in scope, the window widens (unbounded if never processed) and the cumulative redistribution grows.
  This is **environmental, not attacker-controlled** — the attacker **cannot force** keeper downtime.
- **Not High.** No direct protocol-fund loss; no attacker-forced amplification; impact is bounded reward
  redistribution, not a drain.
- **Not invalid / not QA-by-default.** Mechanism, unprivileged reachability, and the zero-sum loss are
  **runtime-confirmed** (P154). It is a real defect, not a false positive.

## The precondition correction (important)
Do **not** frame this as "requires an almost-impossible keeper failure." The baseline precondition is the
**normal gap** between a lock's `unlockTime` and the next keeper sweep, which exists under healthy operation.
Keeper failure is **not** the baseline trigger — it only **widens** an already-existing window.

## Why not higher / why not lower
- Higher (Medium/High) would require either attacker-forced amplification (absent) or protocol-fund loss
  (absent).
- Lower (QA/informational) would require the loss to be non-existent or purely theoretical — but a concrete,
  zero-sum, runtime-proven redistribution exists every keeper gap.

## What a human must still decide
The Low↔Medium line and any QA/out-of-scope call depend on the **program's trusted-operator/keeper scope
stance** — see scope_decision_memo.md. This memo recommends Low baseline; it does **not** set the program's
scope.
