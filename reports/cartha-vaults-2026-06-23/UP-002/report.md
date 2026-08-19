# UP-002 — UUPS _authorizeUpgrade is ADMIN-gated on both vaults and the factory; implementations call _disableInitializers; BeaconProxy init is atomic (honest negative)

> **DISPOSITION: REJECTED — honest negative (NOT a vulnerability).** Investigated and cleared; included for audit completeness. Do NOT submit. See Disproof / boundary below.

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Improper Access Control
- **Triage status:** rejected
- **Confidence:** High
- **ICE:** Impact=No unauthorized ownership/role/impl change. · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/CarthaVault.sol:158`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`

## Description

Full UUPS/Beacon review: authorize-gate present and ADMIN-bound on all upgradeable contracts; _disableInitializers on all impls; BeaconProxy makes child/parent init atomic; reinitializeV2 is role-gated and version-gated; no selfdestruct/arbitrary-delegatecall. Honest negative. Residual centralization (beacon owner can flip implementation for all proxies; ADMIN can upgrade) is the intended trust model.

## Impact

None beyond the intended ADMIN/beacon-owner trust assumption.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Take over a vault by calling initialize on a fresh proxy first, by upgrading to a malicious impl, or by re-initializing to reset roles/asset.
- **Technique:** Tried: (a) call initialize on a child/parent proxy post-deploy — reverts, initialize ran atomically inside BeaconProxy constructor (initializer consumed); (b) call initialize on the implementation directly — reverts, _disableInitializers; (c) call upgradeToAndCall on a vault — reverts unless msg.sender has ADMIN; (d) call reinitializeV2 — reverts unless ADMIN and only once.
- **Evasion:** Defenses complete: atomic deploy+init via BeaconProxy, _disableInitializers on impls, ADMIN-gated _authorizeUpgrade, reinitializer(2)+ADMIN on the V2 hook.

## Reachability / follow-up

reachable: upgrade/init paths. no_privileged_keys: n/a. state_before_after: n/a. why_guards_fail: it does not. scope_match: none.

## Triage reasoning

UUPS _authorizeUpgrade is ADMIN-gated on both vaults and the factory; all impls _disableInitializers(); BeaconProxy deploy+init is atomic (no front-run window); reinitializeV2 is ADMIN + reinitializer(2). Honest negative (cleared with disproof).

## Disproof / boundary

_authorizeUpgrade is `onlyRole(Roles.ADMIN)` in CarthaVault, CarthaParentVault and CarthaVaultFactory; constructors call _disableInitializers() so impls cannot be initialized directly; deployVault/deployParentVault create the BeaconProxy with initData in the same call (deploy+init atomic), leaving no front-run window; reinitializeV2 is reinitializer(2) + ADMIN. No selfdestruct or arbitrary-delegatecall sink.
