# DOS-003 — withdraw / releaseFromParent revert when ANY single active child reverts on withdrawToParent (no per-child isolation in _withdrawFromChildren)

- **Severity (recommended):** Medium
- **Category (HackenProof VRT):** DoS with (Unexpected) revert
- **Triage status:** submit
- **Confidence:** Medium
- **ICE:** Impact=Medium · Confidence=Medium · Exploitability=Conditional
- **Location(s):** `src/CarthaParentVault.sol:473-500,145-164,456-470`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`

## Description

_withdrawFromChildren (473-500) loops active children and calls ICarthaVault(vault).withdrawToParent(withdrawAmount) for each with no try/catch. withdrawToParent is onlyRole(KEEPER_BOT) and has no whenNotPaused, so it works on a paused child today; however if a future child implementation, a malicious child added by ADMIN, or a child whose asset transfer reverts (e.g. the parent loses KEEPER_BOT role on one child, or a non-standard asset) reverts inside this loop, the entire parent withdraw()/releaseFromParent()/_prepareSharePayout reverts, head-of-line blocking ALL parent withdrawals even though other children could have satisfied the request. Severity is Medium/Medium-confidence because under the current single-asset (USDC) + parent-holds-KEEPER_BOT-on-every-child configuration no concrete revert path is reachable, but the pattern (external call in a loop with no failure isolation) is a latent protocol-wide DoS the moment a child can revert.

## Impact

One reverting child in the withdraw loop blocks all parent withdrawals/releases. Latent under current config; becomes a live protocol-wide freeze if any child can revert withdrawToParent (lost role, malicious/odd child, asset change).

## Attack path (Intent / Technique / Evasion)

- **Intent:** Block all parent withdrawals by making one child's withdrawToParent revert.
- **Technique:** A child for which withdrawToParent reverts (parent not KEEPER on it, malicious child, reverting asset) sits in vaultList; _withdrawFromChildren reverts the whole tx instead of skipping that child.
- **Evasion:** No try/catch around the per-child external withdrawal; failure is not isolated, unlike processQueuedWithdrawals which uses continue.

## Reachability / follow-up

reachable: when any active child reverts on withdrawToParent. no_privileged_keys: trigger is child state. state_before_after: one child revert -> whole parent withdraw reverts. why_guards_fail: no try/catch. scope_match: core liveness.

## Triage reasoning

_withdrawFromChildren / removePool loop call child.withdrawToParent with no per-child failure isolation; one reverting/paused child head-of-line-blocks all parent withdrawals. Related to DOS-001 (same no-try/catch class, write-path). Latent under the current USDC + trusted-children config but a real isolation gap.
