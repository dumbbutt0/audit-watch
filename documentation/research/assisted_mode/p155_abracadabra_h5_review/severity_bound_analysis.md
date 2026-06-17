# P155 — Gate 4: Impact & Severity Bound

| Item | Finding |
|---|---|
| Affected asset | Reward token(s) distributed via `notifyRewardAmount` (any of up to `MAX_NUM_REWARDS=5`). |
| Who loses | Honest stakers (unlocked stakers and still-locked stakers) — their reward share is diluted. |
| Who gains | The expired-but-unprocessed locker (keeps boosted weight). |
| Zero-sum among stakers? | **Yes** — P154 asserted A's over-accrual == B's loss exactly (174.999…e18 each). |
| Protocol funds lost? | **No** — only reward redistribution among stakers; no principal/protocol-fund loss. |
| Scales with reward rate? | Yes — proportional to rewards distributed in the post-expiry window. |
| Scales with operator delay? | **Yes — the dominant factor.** ~0 if processed at `unlockTime`; grows each unprocessed epoch. |
| Scales with expired locked size? | Yes — larger expired lock = larger boosted share. |
| Scales with multiplier? | Yes — higher `lockingBoostMultiplerInBips` = larger over-share (3× in the PoC; configurable higher). |
| Scales with # expired locks / pool weight? | Yes — more expired-unprocessed weight vs honest weight = larger redistribution. |
| Can the loss continue indefinitely? | **Yes** — unbounded if the operator never processes (no on-chain bound, no user remedy). |
| Repeatable / compoundable? | Yes — persists every epoch until processing; affects every distribution in the window. |
| Does claiming finalize the misallocation? | **Yes** — `_getRewards` pays/locks the accrued (mis-)amount; later processing corrects only future windows, not already-accrued/claimed ones. |

## Severity recommendation: **Medium candidate**
Reasoning: a **real, repeatable, zero-sum loss to honest third-party stakers** who have **no self-remediation**
(pushes up from Low/QA), but **no protocol-fund loss**, magnitude **bounded by trusted-operator liveness**, a
**documented maintenance cadence**, and an **inherited well-known design** (Convex/Curve) (pushes down from
High). Net: **Medium**, with an explicit downgrade path to **Low/QA** if the program treats the operator as
fully trusted / routine maintenance as assumed (a scope call deferred to the human). Not High: no
protocol-fund loss and the impact is contingent on operator negligence rather than an always-on primitive.
