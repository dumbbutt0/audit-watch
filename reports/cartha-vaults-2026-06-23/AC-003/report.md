# AC-003 — DiamondInit.init(admin) is external and unguarded but is NOT reachable to grant ADMIN on the live Diamond (honest negative)

> **DISPOSITION: REJECTED — honest negative (NOT a vulnerability).** Investigated and cleared; included for audit completeness. Do NOT submit. See Disproof / boundary below.

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Improper Access Control
- **Triage status:** rejected
- **Confidence:** High
- **ICE:** Impact=No consumer in the live system reads the orphan DiamondInit's storage. · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/diamond/DiamondInit.sol:8`
- **Vulnerable files (bundled in `sources/`):** `DiamondInit.sol`

## Description

Assessed per the deep-analysis prompt: DiamondInit.init has no access control and writes roles[Roles.ADMIN][admin]=true. The concern is whether an attacker can call it to mint themselves ADMIN. Re-derived from source: the diamond-storage slot is contract-local, init's selector is unregistered as a facet, and the only Diamond-context delegatecall path (diamondCut) is contractOwner-gated. A direct call only mutates the orphan DiamondInit contract's storage. Not exploitable. (Note: contractOwner — set in Diamond's constructor and movable only via LibDiamond.setContractOwner, which is itself only invoked from the constructor; there is NO transferOwnership facet wired, so ownership is effectively immutable post-deploy. That is a separate operational rigidity, not an access-control bug.)

## Impact

None — direct calls only affect a throwaway contract; the live Diamond's roles[ADMIN] is unreachable except by the existing contractOwner.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Attempt to self-grant Roles.ADMIN on the live access-control Diamond by calling the unguarded DiamondInit.init.
- **Technique:** Attacker calls DiamondInit(deployedInit).init(attacker) directly, OR tries to reach init through the Diamond fallback. Direct call writes to DiamondInit's own storage; Diamond fallback has no selector mapping for init (it was never added in a cut), so it reverts 'Function does not exist'.
- **Evasion:** Diamond-pattern storage isolation (contract-local DIAMOND_STORAGE_POSITION) plus the fact that init is only ever delegatecall'd from the contractOwner-gated diamondCut path means the init writes never land in the Diamond unless the owner triggers them. The 'missing access control' on init is harmless because the storage it touches is not the Diamond's unless invoked via the gated path.

## Reachability / follow-up

reachable: init() callable directly. no_privileged_keys: n/a. state_before_after: a direct call mutates DiamondInit's own (throwaway) storage, not the Diamond's. why_guards_fail: it does not — see disproof. scope_match: none.

## Triage reasoning

DiamondInit.init(admin) is external and unguarded but NOT exploitable on the live Diamond. Cleared with disproof (safety-net init code, so a concrete attacker-path disproof is provided).

## Disproof / boundary

To grant ADMIN on the live Diamond an attacker needs init() to execute in the Diamond's storage context. (1) LibDiamond.diamondStorage() is contract-local; calling init() directly on the DiamondInit contract writes DiamondInit's own storage slot, which nothing reads. (2) init's selector is never registered as a facet function (only diamondCut is added in the Diamond constructor), so the Diamond fallback cannot route to it. (3) The only path that delegatecalls init in the Diamond's context is LibDiamond.diamondCut -> initializeDiamondCut, and diamondCut is gated by enforceIsContractOwner. All three barriers must break; none do.
