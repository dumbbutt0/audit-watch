# P155 — Gate 1: Source Intent & Expected Behavior

All citations from `audits/abracadabra-2024-03-holdout/contracts/src/staking/LockingMultiRewards.sol`
(md5 `74937ac70403a79dff31bbc8d427e87c`, unchanged).

| Question | Evidence | Reading |
|---|---|---|
| Should expiry affect reward weight? | Boost is described as the reward for locking: "Stakers can lock their tokens **for a period of time** to get a boost on their rewards" (:9-10). The boost is tied to the lock *period*; once the period ends the rationale for the boost ends. | Implies expiry **should** end the boost — but the code only ends it on processing. |
| Is operator processing intended to be prompt? | `processExpiredLocks` NatSpec: "Should be called **once a `rewardDuration`** (for example, every week)" (:395-396). | Prompt-ish processing is the **documented expectation** — but it is an off-chain expectation, not enforced on-chain. |
| Is delayed processing tolerated / intended? | The de-boost happens **only** inside `processExpiredLocks` (:441-445), which is `onlyOperators` (:397). The lazy, operator-driven expiry model is **inherited**: "Based from Curve MultiRewards / Ellipsis EpsStaker / **Convex CvxLockerV2**" (:11-13). | The architecture **delegates** de-boost to the operator by design (Convex/Curve lineage) → some delay is structurally tolerated. |
| Do users have a self-remediation path? | `withdraw`/`lock` only touch `unlocked` (:170-184,:155); there is **no** user-callable function that releases an expired lock or removes its boost. Only the operator can (`processExpiredLocks`). | Users **lack** self-remediation. Aggravating: the over-accrual is structural, not the user's opt-in. |
| Is there a spec/test asserting expected post-expiry weight? | No in-repo test or spec for `LockingMultiRewards` (only the P154 PoC). | No authoritative expected-behavior oracle beyond NatSpec. |

## Verdict: **intent_ambiguous**
The NatSpec ties the boost to the lock *period* and expects prompt processing (→ persistent post-expiry
boost looks like a defect), yet the inherited Convex/Curve architecture deliberately delegates de-boost to
an operator (→ some persistence is by design). The two signals point in opposite directions and there is no
authoritative test/spec to break the tie. Unlike P149, this ambiguity is about *whether the resulting loss
is an accepted tradeoff*, not about whether the mechanism/attacker model exists — so it bounds severity/scope
rather than refuting the candidate.
