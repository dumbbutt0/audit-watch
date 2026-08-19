# AC-004 — ADMIN can grant itself EJECTOR / FORCE_EXITER and bypass merkle-list intent (within the ADMIN trust boundary)

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Privilege Escalation
- **Triage status:** downgraded
- **Confidence:** High
- **ICE:** Impact=No escalation path from a non-ADMIN role to ADMIN. · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/diamond/facets/AccessControlFacet.sol:9`
- **Vulnerable files (bundled in `sources/`):** `AccessControlFacet.sol`

## Description

Full authority map re-derived: contractOwner (Diamond) controls diamondCut (add/replace/remove facets, run init delegatecalls) and is effectively immutable post-deploy. roles[ADMIN] (separate mapping, seeded by DiamondInit via the owner's deploy cut) controls grant/revoke of all roles, every vault/factory config setter, merkle roots, pause/unpause, and UUPS upgrades. EJECTOR = lock-signature signer + child forceExit/forceExitUnderperformer caller. KEEPER_BOT = deployToPool/recallFromPool, processQueuedWithdrawals, depositFromParent/withdrawToParent, rebalance/shiftLiquidity. FACTORY (or ADMIN) = deployVault/deployParentVault. RESCUER = rescueFunds (see AC-001). FORCE_EXITER = parent executeForceExit (see AC-002). No public/external state-mutating function was found missing a role/owner check except the intentionally-open ones: setAutoLock (sets only msg.sender's own flag — safe), renounceRole (self only — safe), the user lock/release/extend family (self-position-scoped), and the unguarded-but-unreachable DiamondInit.init (AC-003). Two privilege keys (contractOwner vs ADMIN) are deliberately separated for the diamond-cut vs role-grant split.

## Impact

None beyond the existing ADMIN trust assumption (ADMIN can already upgrade all vaults). No lower role can reach ADMIN.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Determine whether any role can escalate to a higher-privilege role (e.g. KEEPER_BOT/RESCUER -> ADMIN, or ADMIN -> EJECTOR to forge lock signatures).
- **Technique:** Enumerate every function that writes roles[role][account]: only AccessControlFacet.grantRole/revokeRole (ADMIN-gated) and renounceRole (self). No KEEPER/RESCUER/EJECTOR/FACTORY/FORCE_EXITER function writes the roles map, so none can escalate. ADMIN self-granting EJECTOR/FORCE_EXITER is permitted by design and is dominated by ADMIN's existing upgrade power.
- **Evasion:** The intended model is ADMIN-as-superuser; the only protection against ADMIN abuse is off-chain (multisig/timelock), which is out of scope of the on-chain code. Not a code-level gap.

## Reachability / follow-up

reachable: ADMIN grantRole(self). no_privileged_keys: NO. state_before_after: ADMIN gains EJECTOR. why_guards_fail: by design. scope_match: centralization disclosure.

## Triage reasoning

ADMIN can grant itself EJECTOR/FORCE_EXITER and bypass merkle-gated force-exit. This is by design and is strictly dominated by ADMIN's existing powers (UUPS upgrade, set pricing oracle). Documented centralization disclosure, not a separate vulnerability.
