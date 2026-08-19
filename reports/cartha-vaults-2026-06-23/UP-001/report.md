# UP-001 — erc7201 storage locations for CarthaVault / CarthaParentVault / CarthaVaultFactory are correct and isolated; the parent's hardcoded ERC4626 asset slot does not collide (honest negative)

> **DISPOSITION: REJECTED — honest negative (NOT a vulnerability).** Investigated and cleared; included for audit completeness. Do NOT submit. See Disproof / boundary below.

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Other
- **Triage status:** rejected
- **Confidence:** High
- **ICE:** Impact=No mis-read/mis-write of any state variable. · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/CarthaParentVault.sol:91`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`

## Description

Audited all three erc7201 declarations and the parent's manual ERC4626-slot trick. All hardcoded constants match their keccak derivations (so a tooling/typo slot-misplacement bug is ruled out), and every namespace used by each contract is mutually disjoint. The hardcoded asset slot collides with nothing in the parent's actual storage graph. Honest negative.

## Impact

None — storage namespaces are correct and non-overlapping.

## Reachability / follow-up

reachable: n/a. no_privileged_keys: n/a. state_before_after: n/a. why_guards_fail: it does not. scope_match: none.

## Triage reasoning

erc7201 storage locations and the parent's hardcoded ERC4626 asset slot are correct and collision-free; honest negative (safety-net storage class, cleared with disproof).

## Disproof / boundary

All three erc7201 constants were recomputed and match keccak256(abi.encode(uint256(keccak256(<id>))-1)) & ~0xff exactly. The parent's hardcoded asset slot 0x0773e532...4e00 equals the OZ openzeppelin.storage.ERC4626 base and is disjoint from the ParentVaultStorage / ERC20 / EIP712 / Pausable / Initializable namespaced bases; the parent does not inherit ERC4626 so the single reserved word cannot collide.
