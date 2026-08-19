# LG-002 — depositAndLock bypasses the EIP-712 signature gate entirely; the 'miner-only' lock control is purely off-chain (signature gates no on-chain effect)

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Improper Authentication
- **Triage status:** downgraded
- **Confidence:** High
- **ICE:** Impact=Low · Confidence=High · Exploitability=Permissionless
- **Location(s):** `src/CarthaVault.sol:167-246,212-221,955-963; src/CarthaParentVault.sol:509-548,564-581`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`, `CarthaParentVault.sol`

## Description

lock() (167-199) verifies an EIP-712 LockRequest signed by an EJECTOR and consumes a per-user nonce, intended to bind a Bittensor hotkey and enforce that only verifier-approved miners create positions. But depositAndLock() (204-210) creates a byte-for-byte identical Position (same _createPosition, same shares/lock mechanics) with NO signature, NO hotkey, NO nonce. The hotkey is never stored on-chain in either path (it is only emitted in LockCreated for lock(), and bytes32(0) for the parent's depositAndLockSpread); _createPosition does not persist hotkey at all. Therefore: (a) the signature provides ZERO additional on-chain protection over the permissionless depositAndLock path — any address can self-register a position and become an on-chain LP; the 'miner approval' is enforced only by off-chain validators choosing whether to score the emitted hotkey. (b) The 'front-run a miner's signed lock by occupying the (owner,poolId) slot' grief does NOT hold: lockId = keccak256(msg.sender, poolId) is keyed on the depositor's own address (219,955-963), so an attacker cannot create a position at a victim miner's lockId — PositionAlreadyExists can only be self-inflicted (a miner calling depositAndLock before their own lock()). No third party can block a miner's slot. Reported as Low/design-clarity: the on-chain code does not enforce miner-gating, so any access-control assumption that 'only signed miners hold positions' is false on-chain.

## Impact

No fund loss. The verifier-signature path enforces nothing on-chain that depositAndLock does not already permit; miner exclusivity is off-chain-only. Slot-occupation griefing against a miner is not possible (self-keyed lockId).

## Attack path (Intent / Technique / Evasion)

- **Intent:** Bypass the verifier-signature 'miner-only' gate to hold a vault position without approval.
- **Technique:** Call depositAndLock(poolId, amount>=min, lockDays) directly — no signature, no hotkey, no nonce; an identical position is created.
- **Evasion:** The signature/nonce/hotkey are not load-bearing for any on-chain state; the parallel unsigned entrypoint makes the gate advisory only.

## Reachability / follow-up

reachable: depositAndLock by anyone. no_privileged_keys: permissionless. state_before_after: position created without a signature. why_guards_fail: dual path; sig gates nothing on-chain. scope_match: design/intent.

## Triage reasoning

depositAndLock fully bypasses the EIP-712 signature/hotkey/nonce, so the 'miner-only' gate has NO on-chain effect (hotkey is emitted, never stored). The 'front-run a miner's position slot' grief does NOT hold (lockId is keyed on msg.sender, so PositionAlreadyExists is self-inflicted only). Design/documentation issue: on-chain, miner eligibility is unenforced. Low.
