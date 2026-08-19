# LG-004 — processAutoLocks re-locks an expired position (resets start), silently re-imposing a full lock on a user who intended to withdraw

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** downgraded
- **Confidence:** High
- **ICE:** Impact=Low · Confidence=High · Exploitability=Privileged-trigger (KEEPER) + user opt-in
- **Location(s):** `src/CarthaVault.sol:791-821,280-293,540-560`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`

## Description

processAutoLocks (800-821) is KEEPER-gated and, for owners with autoLockEnabled, an existing non-pending expired position, resets position.start = now and cooldownEnds = now+cooldown and lastEpoch (814-817). It correctly skips positions with pendingWithdrawal (809) so it cannot strand an already-queued withdrawal. However a user who enabled autoLock and whose lock just expired, but who has NOT yet called requestRelease (e.g. intends to call release() directly), can be front-run by the keeper's processAutoLocks: the position re-locks, and the user's subsequent release()/requestRelease() reverts PositionLocked / continues to be uncallable for another full lockDays. The user opted into autoLock via setAutoLock, and can disable it (setAutoLock(false) is unguarded, 791-795), so this is a self-service/Low liveness issue — but disabling and exiting is a race against the keeper, and there is no on-chain guarantee the user wins. Note also: release()/requestRelease() do NOT require pendingWithdrawal, so the documented two-step (requestRelease then process) is optional — direct release is the primary path and is the one exposed to the autolock race.

## Impact

An autoLock-enabled user can be re-locked by the keeper for another full term in the window between expiry and their exit call, blocking withdrawal. Self-mitigable (disable autoLock) but racy; Low.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Re-lock a user who intended to exit, delaying their withdrawal by a full lock term.
- **Technique:** Keeper calls processAutoLocks([user]) in the expiry window before the user's release(); position.start resets -> release() reverts PositionLocked.
- **Evasion:** autoLock skips pendingWithdrawal but not the direct-release path; no monotonicity/consent check that the user still wants to remain locked at the moment of renewal.

## Reachability / follow-up

reachable: keeper processAutoLocks before user release. no_privileged_keys: keeper triggers; user opted into autoLock. state_before_after: position re-locked. why_guards_fail: no user-intent check vs autoLock. scope_match: griefing.

## Triage reasoning

processAutoLocks re-locks an expired non-pending position (resets start); a user who enabled autoLock but intends a direct release() can be keeper-front-run and re-locked for a full term. Racy self-mitigation via setAutoLock(false). It correctly skips pendingWithdrawal, so it cannot strand a queued withdrawal. Low griefing.
