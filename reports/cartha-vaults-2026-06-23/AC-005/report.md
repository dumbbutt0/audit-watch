# AC-005 — EJECTOR-signed LockRequest binds owner/poolId/amount/lockDays/hotkey/timestamp/nonce; child & parent merkle leaves are second-preimage-safe (honest negative)

> **DISPOSITION: REJECTED — honest negative (NOT a vulnerability).** Investigated and cleared; included for audit completeness. Do NOT submit. See Disproof / boundary below.

- **Severity (recommended):** Info
- **Category (HackenProof VRT):** Improper Authentication
- **Triage status:** rejected
- **Confidence:** High
- **ICE:** Impact=No unauthorized lock or force-exit. · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/CarthaVault.sol:1200`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`

## Description

Verified the two signature surfaces and the three merkle-leaf surfaces for missing-binding, replay, malleability, and second-preimage issues. All outcome params are signed; owner is pinned to msg.sender; nonce+chainid+verifyingContract+deadline all present; leaves are fixed-width and root-gated to ADMIN. ECDSA.recover is OZ v5 (rejects high-s malleability and address(0) via the OZ recover error path). Honest negative.

## Impact

None.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Replay or re-scope an EJECTOR lock signature, or forge a merkle leaf to force-exit a non-listed user.
- **Technique:** Tried: (a) replay a captured lock sig from another address — blocked, owner is pinned to msg.sender and is inside the hash; (b) replay across chains/vaults — blocked, EIP-712 domain binds chainid+contract; (c) replay same chain — blocked, per-signer nonce incremented pre-effect; (d) craft a leaf colliding with an internal node — blocked, fixed 64-byte leaf preimage.
- **Evasion:** Defenses are complete: signed-field set == consumed-field set, owner==msg.sender pin, nonce+domain+deadline, ADMIN-gated non-zero roots, fixed-width leaves.

## Reachability / follow-up

reachable: lock()/lockAndSpread(). no_privileged_keys: n/a. state_before_after: nonce consumed. why_guards_fail: it does not. scope_match: none.

## Triage reasoning

Honest negative: the EIP-712 lock signature (child + parent) is correctly bound and non-replayable. Cleared with disproof.

## Disproof / boundary

The digest = _hashTypedDataV4(structHash) binds chainId + verifyingContract (OZ EIP712Upgradeable), owner is pinned to msg.sender, nonce is per-owner monotonic (depositNonces/lockNonces incremented after use), and poolId/category are in the struct. The hand-rolled assembly structHash in CarthaVault matches the typehash field order byte-for-byte; the parent uses abi.encode. Cross-owner/cross-nonce/cross-vault/cross-chain replay are all foreclosed. The only residual is a missing future-timestamp lower bound, but the timestamp is chosen by the trusted EJECTOR signer.
