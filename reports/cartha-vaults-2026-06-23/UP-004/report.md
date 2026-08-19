# UP-004 — No selfdestruct, no storage-slot collision with ERC-1967 admin/impl/beacon slots in any implementation (honest negative)

> **DISPOSITION: REJECTED — honest negative (NOT a vulnerability).** Investigated and cleared; included for audit completeness. Do NOT submit. See Disproof / boundary below.

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Other
- **Triage status:** rejected
- **Confidence:** High
- **ICE:** Impact=No impl destruction, no proxy-slot overwrite. · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/CarthaParentVault.sol:125`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`

## Description

Swept for selfdestruct, arbitrary delegatecall, and ERC-1967 reserved-slot collisions across the diamond and the three upgradeable implementations. None present. Honest negative.

## Impact

None.

## Reachability / follow-up

reachable: n/a. no_privileged_keys: n/a. state_before_after: n/a. why_guards_fail: it does not. scope_match: none.

## Triage reasoning

No selfdestruct, no arbitrary-delegatecall sink, no collision with the ERC-1967 impl/admin/beacon slots. Honest negative.
