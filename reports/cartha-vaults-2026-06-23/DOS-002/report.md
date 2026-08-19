# DOS-002 — releaseFromParent / release permanently un-callable when child funds are GM-deployed and the keeper never recalls (trusted-keeper liveness)

- **Severity (recommended):** Medium
- **Category (HackenProof VRT):** DoS with (Unexpected) revert
- **Triage status:** submit
- **Confidence:** High
- **ICE:** Impact=Medium · Confidence=High · Exploitability=Conditional (requires liquidity to be GM-deployed; trigger is keeper inaction/withholding)
- **Location(s):** `src/CarthaParentVault.sol:431-442,456-470,625-659,664-704; src/CarthaVault.sol:280-337,513-531`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`, `CarthaVault.sol`

## Description

Parent exits route through _prepareSharePayout (456-470): needed = shareValue - idleParentUSDC; if needed>0 it requires _availableFromChildren()+10 >= needed else returns sufficient=false and releaseFromParent reverts InsufficientVaultBalance (647). _availableFromChildren() (431-442) ONLY counts each child's idle USDC balance (balanceOf(child)); it does NOT count the child's GM-deployed value. When the KEEPER_BOT has deployed child USDC into the 0xM pool (deployToPool) so child idle ~ 0, a parent user whose lock+cooldown have expired CANNOT exit: requestReleaseFromParent only sets the flag, and processQueuedParentWithdrawals likewise calls _prepareSharePayout and `continue`s on insufficient. The user's only path to funds is for a trusted KEEPER to first recallFromPool (async, multi-tx, 0xM-keeper-dependent) and re-idle the USDC. The child-level release() (313-314) has the identical trap: payout>vaultBalance reverts InsufficientVaultBalance when the child's USDC is GM-deployed. There is no permissionless force-recall and no emergency exit; getting funds out is entirely gated on keeper liveness/honesty.

## Impact

Censorship / liveness risk: a stalled, offline, or adversarial keeper can indefinitely block any user from withdrawing matured funds whenever liquidity is GM-deployed. Worst case the user's principal is unreachable for an unbounded time despite an expired lock. Bounded to Medium because an honest keeper restores access and no value is destroyed.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Trap matured user funds by keeping liquidity GM-deployed and not recalling.
- **Technique:** Deploy child idle USDC to the 0xM pool (deployToPool) so _availableFromChildren()~0; matured users' releaseFromParent/release then revert InsufficientVaultBalance; only a keeper recall can free funds.
- **Evasion:** Cap-at-idle design (withdrawToParent caps at idle; _availableFromChildren ignores GM value) plus no permissionless recall means the de-risking/exit path depends on a trusted keeper; the lock/cooldown gates are satisfied yet the exit still cannot execute.

## Reachability / follow-up

reachable: yes whenever idle < matured-claim and keeper inactive. no_privileged_keys: user cannot self-recall. state_before_after: user matured but release reverts InsufficientVaultBalance until keeper recalls. why_guards_fail: exit relies entirely on KEEPER_BOT recall. scope_match: core liveness.

## Triage reasoning

releaseFromParent/release are un-callable when child funds are GM-deployed and the keeper has not recalled: _availableFromChildren counts only child IDLE USDC, so a matured user cannot exit without a trusted keeper recall + processQueued. No permissionless/emergency exit path. Liveness/censorship risk dependent on keeper.
