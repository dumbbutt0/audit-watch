# P155 — Gate 2: Attacker Model

| Question | Answer | Basis |
|---|---|---|
| Can a normal user create the boosted lock? | **Yes** | `stake(amount, true)` / `lock(amount)` are public, `whenNotPaused`, no role (:150,:155). |
| Can the user passively benefit after expiry? | **Yes** | After `unlockTime`, `bal.locked` is unchanged until processing, so `balanceOf` stays boosted and `earned` keeps accruing at the boosted weight (P154 W2-unprocessed). No further action needed. |
| Does the user need privileged access? | **No** | Ordinary EOA; no owner/operator role. |
| Does the user need to block the operator? | **No** | The benefit accrues during any window before the operator processes; the user does nothing to prevent processing. (A negligent/slow operator increases magnitude but is not caused by the user.) |
| Does the user need to manipulate time, rewards, or processing? | **No** | The user only relies on ordinary time passing + the operator distributing rewards (`notifyRewardAmount`) in the post-expiry window — both normal production conditions. |
| Can honest users force processing / remove the expired boost? | **No** | `processExpiredLocks` is `onlyOperators` (:397); no user-callable de-boost exists. Honest stakers cannot protect their share. |
| Is the attacker action simply "lock, wait past expiry, claim while unprocessed"? | **Yes** | That is the whole flow; no exploit primitive beyond ordinary staking + waiting. |

## Verdict: **unprivileged_passive_benefit**
The beneficiary is any ordinary locker; the benefit is passive (it accrues by inaction once a lock expires)
and the loss falls on honest stakers who have no on-chain way to stop it. The attacker model does **not**
depend on privilege, time manipulation, reward manipulation, or blocking the operator — which is why the
Gate-1 intent ambiguity bounds severity/scope rather than collapsing the model.
