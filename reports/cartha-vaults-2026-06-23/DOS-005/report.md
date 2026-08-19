# DOS-005 — _distributeToChildren reverts the entire lock when all weighted pools are paused (NoActivePools) — parent deposits blocked by child pauses

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** DoS with (Unexpected) revert
- **Triage status:** downgraded
- **Confidence:** High
- **ICE:** Impact=Low · Confidence=High · Exploitability=Privileged (pause/weight control)
- **Location(s):** `src/CarthaParentVault.sol:404-428,252-299,348-365,557-562`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`

## Description

_distributeToChildren (404-428) computes totalWeight summing only active AND non-paused children, and reverts NoActivePools if totalWeight==0. It is called from _pullMintAndDistribute on every lockAndSpread / depositAndLockSpread / lockTopUp. If ADMIN/keeper pauses (or removes) all children that carry weight, every parent deposit reverts — depositors cannot enter even though the parent itself is healthy. Also, _rebalanceToWeights and _distributeToChildren count totalWeight over active+non-paused pools while totalAssets() counts isActive pools regardless of pause, so a paused-but-active child's previously-deposited value is still in totalAssets() but receives no new distribution — a paused child with weight silently shifts new deposits onto the remaining pools (concentration), and if none remain, deposits brick. Low because it is recoverable by unpausing/re-weighting and affects deposits (entry), not exits.

## Impact

Parent deposits revert when every weighted child is paused; concentration of new deposits onto unpaused children otherwise. Recoverable; entry-side only.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Block parent deposits by pausing all weighted children.
- **Technique:** Pause every child with non-zero weight -> totalWeight==0 in _distributeToChildren -> NoActivePools revert on every lockAndSpread/depositAndLockSpread/lockTopUp.
- **Evasion:** Distribution requires at least one active non-paused weighted pool; no fallback to hold the deposit idle in the parent.

## Reachability / follow-up

reachable: only when all weighted children paused. no_privileged_keys: pause is ADMIN. state_before_after: deposit reverts. why_guards_fail: no idle-hold fallback. scope_match: deposit liveness.

## Triage reasoning

_distributeToChildren reverts NoActivePools if all weighted children are paused, bricking parent deposits while paused. Operational/liveness edge; deposits resume when a child unpauses. Low.
