 `Note: Not all issues are guaranteed to be correct.`


# Broken inline-assembly parsing in _verifyBridgedData: misaligned mload, off-by offsets, missing masking and bounds checks allow verification bypass and message forgery
****
- Severity: Critical


## Targets
- _verifyBridgedData (VerifyBridgedData)

## Description

Multiple related bugs in VerifyBridgedData._verifyBridgedData arise from incorrect manual parsing of a bytes buffer using inline assembly. The implementation (1) treats the bytes pointer as if it pointed at content instead of accounting for the 32-byte length prefix (missing add(data, 0x20)), (2) advances the assembly cursor with incorrect constants (e.g. add(i,16) where 4 was required, or inconsistent add 20 then add 16), (3) uses mload at unaligned offsets that straddle fields, (4) assigns full 32-byte mload results directly to smaller types without shifting/masking (20-byte address, 4-byte length), (5) mutates the assembly loop index i and later relies on high-level Solidity indexing that assumes a different base, and (6) lacks robust bounds checks that ensure payloadLength fits within data.length before copying. These issues combine to break the correspondence between the values validated by the verifier and the bytes actually forwarded or executed.

## Root cause

Incorrect and inconsistent pointer arithmetic and misuse of mload in handwritten assembly when parsing Solidity bytes: the code fails to skip the 32-byte length slot, uses wrong byte increments (causing off-by-12/ -32 misalignment), does not mask/shift 32-byte words to extract sub-word fields, and mixes assembly-mutated raw offsets with high-level indexing semantics. Parsing happens before authorization and without sufficient bounds checks, making the verifier operate on misaligned or attacker-controlled field values.

## Impact

High — an attacker who can supply crafted bridged messages (or influence the bytes passed into _verifyBridgedData) can: (1) cause the verifier to validate a different selector/payload slice than the one actually forwarded (selector confusion), enabling unauthorized contract calls; (2) cause the parsed target address to be incorrect or attacker-controlled, routing messages to unintended recipients; (3) manipulate payloadLength to trigger truncated/oversized copies or out-of-bounds reads that lead to reverts (DoS) or memory-corruption-style inconsistencies; and (4) bypass zero-address or minimum-length checks by presenting values at the misaligned read positions. Practically, these allow forgery of bridged messages, unauthorized execution of whitelisted targets/selectors, theft or misrouting of funds, and denial-of-service of message processing.

---

# Unsafe manual parsing + message execution allows message forgery and self-call access-control bypass
****
- Severity: Critical


## Targets
- _processData (BridgeMessenger)
- changeSourceGovernor (WormholeMessenger)

## Description

Bridge message handling combines incorrect handwritten assembly parsing of bytes buffers with an execution path that performs attacker-controlled calls. The parser (BridgeMessenger._processData) uses mload(add(data, i)) without accounting for the 32-byte length prefix, advances/updates offsets inconsistently in assembly, and fails to shift/mask 32-byte words into smaller fields (addresses, lengths). It also mutates an assembly index and then uses high-level Solidity indexing, mixing incompatible offset bases. As a result, values validated or extracted by the verifier (target, value, payloadLength, selector) can be misread, and the bytes actually forwarded in target.call{value}(payload) can differ from what was intended or checked. Because the contract executes arbitrary target.call(payload) entries parsed from the untrusted buffer, an attacker can craft a bridged message that causes the contract to call itself (target == address(this)) with a payload that encodes protected functions (e.g., changeSourceGovernor). Those functions protect themselves by requiring msg.sender == address(this); the message-driven self-call satisfies that check and allows unauthorized changes.

## Root cause

Unsafe, inconsistent manual parsing of Solidity bytes in inline assembly combined with an execution primitive that performs untrusted-directed calls. The parser: (1) omits the 32-byte bytes.length prefix when computing mload addresses, (2) reads 32-byte words and assigns them directly to sub-word fields without shifting/masking, (3) updates and uses offsets inconsistently between assembly and Solidity indexing, and (4) lacks robust bounds/length checks. The executor then honors parsed target/value/payload without additional origin binding or attestation, enabling attacker-controlled self-calls.

## Impact

High — an attacker able to supply or influence the incoming bridged bytes (or cause the contract to accept a crafted message) can: (1) forge bridged messages whose parsed target or selector differs from the bytes that were validated, enabling unauthorized forwarding to unintended addresses; (2) cause the contract to perform self-calls that satisfy msg.sender == address(this) protections and therefore invoke functions intended to be "internal-only" (e.g., changeSourceGovernor), enabling takeover of message-source validation or other privileged state changes; (3) mis-route funds or trigger arbitrary calls via corrupted value/payload fields; and (4) induce truncated/oversized copies that lead to reverts (DoS) or inconsistent behavior. These failures can lead to governance/state takeover, unauthorized configuration changes, misdirected funds, and denial-of-service of bridge message processing. `Note: Not all issues are guaranteed to be correct.`


# Signature/Domain Binding and Validator Discovery Errors cause broken EIP-712/EIP-1271 flows, invalid signatures, and potential misbound authorizations
****
- Severity: Medium


## Targets
- _verifySignedHash (OperatorSignedHashes)
- getEnableModuleTransactionHash (PolySafeCreatorWithRecoveryModule)

## Description

Two related issues break off-chain signature semantics and domain binding: (A) OperatorSignedHashes enforces a brittle, nonstandard 65-byte signature format and repurposes r to encode the validator address, calling the decoded address as the validator with the fixed 65-byte blob; and (B) PolySafeCreatorWithRecoveryModule computes a Safe (proxy) address for EIP‑712 domain/tx hashing using a factory helper but assumes that computed address always equals the actually deployed Safe address. Together these defects disrupt EIP‑1271/EIP‑712 expectations, causing valid contract-signed operations to be rejected, signatures to be tied to the wrong on-chain contract, and authorizations to be misbound or unusable.

## Root cause

Incorrect assumptions about off-chain and on-chain signature/address primitives: (1) OperatorSignedHashes assumes contract validators use the same fixed 65-byte EOAs-style format and can be discovered by decoding the r word, instead of using an explicit validator address and accepting arbitrary-length validator blobs per EIP‑1271; (2) PolySafeCreatorWithRecoveryModule trusts the factory's computeProxyAddress(owner) result as the canonical Safe address without ensuring the factory uses identical inputs/initializer/salt/deployment path, and without verifying that the computed address actually hosts the intended Safe instance. Both rely on brittle, implicit conventions rather than robust validation of the validator identity and domain-binding inputs.

## Impact

High — correctness/availability and potential authorization misbinding:
- Denial-of-service / broken UX: legitimate EIP‑1271 validators that accept variable-length, validator-specific signatures (or any validator that does not expect the r-encoded address) will be rejected by OperatorSignedHashes (length check or unexpected blob), causing valid contract-signed operations to fail.
- Interoperability loss: wallets and external signers expect standard EIP‑1271 semantics; enforcing a 65-byte format or custom encoding forces all validators to implement a nonstandard interface or be unusable.
- Invalid/irrelevant signatures: getEnableModuleTransactionHash can produce EIP‑712 digests bound to a computed proxy address that differs from the real deployed Safe, so signatures created over that digest will be invalid for the actual Safe or, worse, valid for a different contract if an attacker can cause a contract to exist at the computed address.
- Misbound authorizations & surprise control: if an adversary can influence which contract ends up at the computed address, signed enableModule operations (or other EIP‑712 flows) could target an unintended contract, enabling unauthorized module enabling or other privileged setup.
Overall, these lead to rejected valid operations, fragile integrations, and in the worst case signed authorizations that affect the wrong on-chain entity.

---

# Unprotected initializer allows first caller to seize ownership and upgrade control
****
- Severity: Qa


## Targets
- initialize (ServiceManager)
- changeImplementation (ServiceManager)

## Description

The ServiceManager contract exposes an external initialize() that sets owner = msg.sender only if owner == address(0). Because owner is not set during construction and is used as the sole initialization guard, any external account that calls initialize() first (for example on a proxy instance whose implementation constructor did not run) becomes the permanent owner. Owner-only functions (notably changeImplementation and setOperatorWhitelist, among others) trust this owner value and grant privileged capabilities. An attacker who wins the race to call initialize() can immediately exercise owner-only functions, including replacing the implementation pointer, modifying operator whitelists, or otherwise taking administrative control.

## Root cause

The contract relies on an inherited, mutable owner storage slot as the only initialization guard. initialize() lacks an access-control initializer pattern (no initializer modifier, no proxy-only guard, no dedicated immutable initializer flag) and owner is never assigned at deployment. As a result, the first external caller when owner == address(0) can claim ownership. Additionally, privileged setters like changeImplementation perform no further validation (timelock, multi-sig, or implementation sanity checks) beyond the owner check.

## Impact

High / Critical — an attacker who calls initialize() first gains full administrative control of ServiceManager. This allows immediate invocation of owner-only functions such as changeImplementation (enabling arbitrary implementation upgrades to malicious code), setOperatorWhitelist (altering operator permissions), changeOwner, pause/unpause, and any other privileged operations. Consequences include malicious upgrades, censorship, theft or redirection of funds, and permanent protocol compromise.

---

# Inconsistent or missing event emissions allow on-chain signals to diverge from actual state changes
****
- Severity: Qa


## Targets
- recoverAccess (RecoveryModule)
- unbondWithSignature (ServiceManager)
- _claim (StakingBase)
- changeOwner (HashCheckpoint)

## Description

Several places in the codebase emit events (or fail to emit them) in ways that can be inconsistent with the actual on-chain state or with the outcome of preceding external calls. This class of issues manifests as: (1) events emitted unconditionally despite an external call failing or returning false (false success signals), (2) events reporting values that can be different from amounts actually transferred, (3) events that read live storage after potentially reentrant or virtual externalized operations leading to stale/incorrect fields in the event, and (4) ownership/state writes that can occur without the expected event being emitted. Together these lead to on-chain logs that are not a reliable source of truth for the protocol state.

## Root cause

The contract logic assumes event emission and storage reads performed after external calls will always reflect the real outcome. Contributing factors across the instances: unchecked/ignored return values from external calls, overwriting or not preserving values returned by external calls before emitting, emitting events after calling virtual/internal functions that may trigger reentrancy or be overridden (without snapshotting or reentrancy protection), and allowing direct writable state/overridable functions so state can change without routing through event-emitting code paths. In short: improper sequencing and lack of defensive checks or invariants around external interactions and state writes.

## Impact

On-chain events become unreliable: off-chain indexers, monitors, governance tools, reconciliations, automation workflows, and users relying on emitted events can be misled. Specific consequences include: incorrect bookkeeping (mismatched refund amounts), false indications that recovery or ownership transfer succeeded when it did not, recording stale/future-incorrect epoch/nonces for reward claims, and silently missed ownership changes. This can cause reconciliation errors, broken automation, missed alerts, difficulty auditing or detecting malicious control transfers, and loss of trust in event-driven systems. While some cases do not directly grant an attacker additional privileges, they materially increase operational risk and can be chained with other issues to create stealthy or confusing attack patterns.

---

# Inconsistent and misleading hash URI accessors including zero-hash sentinel handling
****
- Severity: Qa


## Targets
- latestHashURI (HashCheckpoint)
- latestHash (HashCheckpoint)

## Description

Two related issues in HashCheckpoint cause callers to receive misleading or inconsistent representations of stored checkpoints: (1) latestHashURI returns a constant-length CID string of 64 ASCII '0' characters when no hash is stored (latestHashes[address] == bytes32(0)), and (2) latestHash and latestHashURI expose the same underlying stored value in different formats—latestHash returns CID_PREFIX + hex(hash) while latestHashURI returns baseURI + CID_PREFIX + hex(hash). Because baseURI is mutable, callers using latestHash will not observe baseURI updates and will receive a different (bare CID) form than callers using latestHashURI. Together these behaviors can mislead callers about existence of a checkpoint and produce inconsistent URIs across consumers.

## Root cause

The contract treats the bytes32(0) sentinel as if it were a valid stored hash rather than explicitly detecting and handling the absent-case. Additionally, two public accessors were implemented to return different representations of the same underlying data (one including the mutable baseURI prefix and one omitting it), creating inconsistent external views. The helper _toHex16 always emits a fixed-length ASCII hex encoding (including for zero inputs), so absent entries are rendered as a non-empty 64-character zero CID instead of a semantic empty/absent result.

## Impact

Logical correctness and UX issues that can cause downstream integration failures and confusion:
- False-positive existence: callers that interpret a non-empty URI as proof that a checkpoint exists may be misled by the 64-zero CID. This can lead to wasted metadata fetch attempts (e.g., attempting to resolve an IPFS CID of zeros), incorrect presence checks, or broken UI/UX.
- Inconsistent resolution: clients using latestHash will receive a bare CID and will not reflect changes to baseURI, while clients using latestHashURI will. When baseURI is changed, different consumers may resolve different URIs for the same address, causing stale or broken content resolution across systems.
- Integration fragility: downstream systems expecting a canonical URI format or relying on absence/presence semantics may behave incorrectly. While this is not directly a funds-extraction vulnerability, it can materially break integrations and user workflows.

---

# Eviction logic treats serviceId == 0 as a sentinel, allowing ID-0 services to escape eviction and causing incorrect removals
****
- Severity: Qa


## Targets
- checkpoint (StakingBase)
- checkpoint / _evict (StakingBase)

## Description

When checkpoint prepares services for eviction it records candidate service IDs into a temporary array at their original service index (a sparse placement) and increments a caller-supplied eviction counter for each flagged entry. If a service has token ID 0, checkpoint writes 0 into the sparse array and still increments the count. The internal helper _evict, however, treats zero as a sentinel (evictServiceIds[i] > 0) and skips zero entries when compacting the sparse array into a contiguous list of evictions. Despite this, _evict uses the original caller-supplied eviction count to drive removal operations (swap-and-pop) on the persistent setServiceIds array. When the supplied count exceeds the number of non-zero entries (because an ID-0 was counted), the removal loop reads uninitialized/default serviceIndexes (zeros) and performs swaps/pops at incorrect indices (commonly affecting index 0). The net result is that the intended ID-0 service remains unstaked and un-evicted, while an unrelated service is removed or the active list ordering is corrupted. Events emitted (ServicesEvicted) may contain zeroed or mismatched fields.

## Root cause

Inconsistent handling of the zero value between producer and consumer: checkpoint treats token ID 0 as a legitimate service identifier and increments the eviction count when it writes a 0 into the sparse evict array, but _evict uses zero as an empty sentinel and ignores zero entries when building the compact eviction list. The design couples a sparse index-based temporary array with a sentinel-based compaction check and relies on an externally-supplied count, rather than using an explicit presence marker or constructing a compact list consistently.

## Impact

High-integrity and availability issues: a service with token ID 0 can evade eviction even after exceeding inactivity thresholds; an unrelated service (often the one at index 0) can be removed from the active set leading to state corruption of setServiceIds; emitted ServicesEvicted events are misleading (zeroed or mismatched fields), breaking off-chain consumers and monitoring. These behaviors enable both bypass of intended eviction and accidental or adversarial corruption/griefing of the active service set, potentially disrupting service availability and accounting.

---

# ETH path omits bond validation allowing creation of services with zero-bond agents
****
- Severity: Qa


## Targets
- create (ServiceManager)

## Description

ServiceManager.create enforces nonzero agent bonds and wraps bonds for non-ETH tokens, but skips these checks when token == ETH_TOKEN_ADDRESS. As a result, callers can create services whose agentParams[] contain bond == 0 when using ETH, unless the downstream IService.create implementation (serviceRegistry) performs equivalent validation. This inconsistent handling permits undercollateralized agents to be registered for ETH-denominated services.

## Root cause

Incorrect branching / missing local validation: the create function assumes the ETH execution path does not require the same nonzero-bond checks (or that the callee will enforce them), so it omits copying/validating/wrapping bond values for the ETH branch. There is no defensive check (e.g., require(agentParams[i].bond > 0)) before delegating to the registry when token == ETH_TOKEN_ADDRESS.

## Impact

Economic and operational risk: agents with zero bond may be admitted to services when using ETH, violating the invariant that agents hold positive collateral. This enables agents to behave maliciously or negligently without financial consequence, undermines slashing/dispute mechanisms, and can enable griefing or denial-of-service attacks. Depending on downstream logic, it can cause loss of funds, incorrect incentive alignment, and reduced reliability of services that assume bonded agents.

---

# Invalid rewardDistributionType handling allows staking with unknown enum -> distributor address(0) call (DoS)
****
- Severity: Qa


## Targets
- _stake and _getRewardReceiversAndAmounts (StakingBase)

## Description

When staking, rewardDistributionInfo encodes (low 8 bits) a RewardDistributionType and (high bits) a distributor address (address = uint160(rewardDistributionInfo >> 8)). _stake validates the address field only when the low-8-bit value equals RewardDistributionType.Custom (requires non-zero address) and otherwise requires the address field to be zero — but it does not reject unknown/invalid low-8-bit values. _getRewardReceiversAndAmounts casts uint8(rewardDistributionInfo) to RewardDistributionType and treats any value that is not Proportional, ServiceOwner or ServiceMultisig as the Custom branch (the final else). As a result, a caller can stake with an invalid low-8-bit value (e.g. uint8 == 4) and high bits == 0, pass _stake validation, and later distribution logic will treat that value as Custom and attempt to call the distributor at address(0) (or call a non-conforming contract), causing external-call failures and reverting reward distribution/claim operations.

## Root cause

Inconsistent handling of rewardDistributionType values: _stake performs insufficient validation (only checking the address when uint8 == Custom but not ensuring the uint8 is a known enum member), while _getRewardReceiversAndAmounts defaults any unknown/invalid enum value to the Custom branch and performs an external call to the encoded address. This mismatch permits invalid enum values with a zero address to be accepted but later invoked as custom distributors.

## Impact

High — denial-of-service or broken reward processing. A malicious or mistaken staker can cause reward distribution/claiming to revert (e.g. by causing a call to address(0) or to a non-conforming contract), preventing rewards from being paid out for that service and potentially blocking user operations that trigger distribution. Depending on how distribution is invoked, this can freeze payouts or cause repeated reverts affecting other users or system processes.

---

# Zero-value bytes32 encoded as valid CID-like URIs leading to metadata collisions and ambiguity
****
- Severity: Qa


## Targets
- tokenURI (ComplementaryServiceMetadata)
- latestHash / latestHashURI (HashCheckpoint)

## Description

Multiple contracts format raw bytes32 storage values directly into CID-like hex strings (CID_PREFIX + 64 hex chars) without treating the zero value as a sentinel for "unset". As a result, unset mapping entries (which default to bytes32(0)) or entries explicitly set to bytes32(0) produce a syntactically valid-looking CID composed of 64 '0' hex characters. This leads to deterministic collisions and ambiguity: different keys (serviceId or address) with no stored hash will resolve to the same URI, and callers cannot distinguish between an absent value and an intentionally stored zero-hash.

## Root cause

Missing defensive validation and inconsistent sentinel handling: tokenURI (ComplementaryServiceMetadata) and latestHash/latestHashURI (HashCheckpoint) unconditionally encode stored bytes32 values into hex CID strings and do not check for bytes32(0). Additionally, the contracts accept and persist bytes32(0) via their setters, so the encoded output is indistinguishable between 'unset' (mapping default) and 'explicitly set to zero'. The helper used to hex-encode 16-byte chunks treats zero bytes as valid data rather than signaling absence.

## Impact

Medium — non-monetary correctness and integrity issues: off-chain consumers (UIs, indexers, search, audits) will see the same zero-CID for multiple distinct keys and may incorrectly infer that content exists or has been published. This causes metadata collisions, misattribution in displays or listings, pollutes indexes, and can break tooling that assumes unique, non-empty URIs per key. Because setter functions allow writing bytes32(0), an authorized actor can intentionally create collisions or effectively erase/overwrite metadata mappings, enabling denial-of-uniqueness or targeted disruption of indexing and display. The issue is read-only from the POV of the view functions but can be weaponized by state writes where permitted.

---

# Packed (operator, serviceId) key truncates serviceId high bits -> nonce collisions and cross-service DoS
****
- Severity: Qa


## Targets
- registerAgentsWithSignature (ServiceManager)
- unbondWithSignature (ServiceManager)

## Description

ServiceManager composes a single uint256 key by placing operator in the low 160 bits and shifting serviceId left 160 bits (operatorService = uint256(uint160(operator)) | (serviceId << 160)) to index per-(operator,service) nonces used for signature replay protection. Because 256 - 160 = 96, the left shift preserves only the low 96 bits of serviceId. serviceId values that differ only in high bits (i.e., that are equal modulo 2**96) map to the same packed key. The same packing pattern is used for at least two nonce maps (mapOperatorRegisterAgentsNonces and mapOperatorUnbondNonces) accessed by registerAgentsWithSignature and unbondWithSignature. As a result, distinct services whose IDs collide modulo 2**96 share a single nonce counter. Although signatures are computed over the full serviceId (so a signature for one full serviceId cannot be directly replayed for a different full serviceId), advancing the shared nonce for one colliding service will invalidate previously-signed messages for the other colliding service(s), causing denial-of-service and broken per-service nonce semantics.

## Root cause

Unsafe manual packing of (operator, serviceId) into a uint256 without (a) enforcing that serviceId fits within the 96 bits implied by the shift, (b) masking serviceId before shifting, or (c) using a collision-free composite key. High bits of serviceId are silently discarded by (serviceId << 160), so serviceId >= 2**96 collides with other serviceIds modulo 2**96.

## Impact

Medium — Availability and integrity impact due to shared nonces across distinct services:  
- Denial-of-Service: An action (e.g., unbondWithSignature or registerAgentsWithSignature) authorized for one colliding service will increment the shared nonce and can cause previously-signed operator-authorized actions for the other colliding service to be rejected. This can block legitimate management flows and, if these flows control funds or agent lifecycle, can disrupt operations.  
- Coordination burden: Operators or service owners must coordinate nonce usage across distinct services that collide, breaking intended isolation.  
- No direct cross-service signature replay: Because signatures include the full serviceId, an attacker cannot straightforwardly replay a signature for one full serviceId to execute it for another full serviceId, but nonce invalidation remains a practical DoS vect0r.  
The vulnerability is exploitable by any party able to trigger signed flows for a serviceId that collides (mod 2**96) with another targeted service.

---

# Rounding mismatch: calculateStakingReward view can under-report reward for eligibleServiceIds[0]
****
- Severity: Qa


## Targets
- calculateStakingReward (StakingBase)

## Description

calculateStakingReward returns sInfo.reward + calculateStakingLastReward(serviceId). calculateStakingLastReward computes each eligible service's share using integer (floor) division: (eligibleServiceRewards[i] * lastAvailableRewards) / totalRewards (or full eligibleServiceRewards[i] if not scaled). The checkpoint() distribution logic performs the same per-index floor divisions but then collects the integer-division remainder (lastAvailableRewards - sum(floor-shares)) and explicitly adds that leftover to the reward for eligibleServiceIds[0] before updating mapServiceInfo. Because calculateStakingLastReward does not include that leftover for index 0, the view returned by calculateStakingReward can be smaller than the reward actually written into mapServiceInfo for eligibleServiceIds[0] by exactly the leftover amount.

## Root cause

Mismatched rounding/leftover handling between the view (calculateStakingLastReward) and the state-updating distribution (checkpoint): the view applies floor division uniformly and never attributes the integer-division remainder to index 0, while checkpoint does add the remainder to eligibleServiceIds[0].

## Impact

Inconsistency between the view and on-chain state: calculateStakingReward can under-report pending rewards for the first eligible service (eligibleServiceIds[0]) by up to the integer-division leftover (a small wei amount). Consequences are primarily correctness and UX/accounting issues (misleading UIs, off-chain accounting discrepancies). There is no direct loss of funds or reentrancy vulnerability implied by this mismatch, but systems relying on the view for precise pending balances may show incorrect values and users could be confused or misinformed.

---

# Ignored execTransaction return value allows silent failure to enable recovery module
****
- Severity: Qa


## Targets
- create (PolySafeCreatorWithRecoveryModule)

## Description

The create function deploys a Safe proxy and then calls ISafe.execTransaction(...) to enable a recovery module on the newly created Safe, but it does not check the boolean return value of execTransaction. In many Gnosis Safe implementations execTransaction returns false (rather than reverting) when the internal call fails (for example, if a guard blocks the call, enableModule reverts, or approvals/signatures are invalid). Because the result is ignored, create continues, emits MultisigCreated and returns an address even when the recovery module was not actually enabled on the Safe. This leads to an on-chain state inconsistent with the expected setup and can break recovery workflows or off-chain assumptions.

## Root cause

The code assumes ISafe.execTransaction will revert on failure. Instead it treats execTransaction as a fire-and-forget call and does not validate its boolean success indicator, allowing failures of the internal Safe call to be silently ignored.

## Impact

- Newly created multisigs may not have the recovery module enabled despite the creator emitting MultisigCreated and returning success.
- Off-chain tooling, operators or users that rely on the event or return value to assume the module is enabled may take incorrect actions, e.g., skip additional setup or assume recoverability.
- Recovery workflows depending on the module could fail, potentially causing loss of intended functionality or increased operational risk.
- The mismatch between emitted event and actual Safe configuration can cause confusion and downstream errors in automation or onboarding flows. `Note: Not all issues are guaranteed to be correct.`
# Improper ERC‑20 allowance handling: zero-first, unchecked approve, and lingering approvals enable DoS and potential theft
****
- Severity: Low

## Targets
- convertToV3 (LiquidityManagerCore)
- increaseLiquidity (LiquidityManagerCore)
- redeem (DefaultTargetDispenserL2)
- _performSwap (BuyBackBurnerUniswap)
- relayToL1Burner (Bridge2BurnerGnosis)

## Description

Several contracts call ERC‑20 approve(...) incorrectly: they set non-zero allowances without first handling existing allowances (zero-then-set or safe increase/decrease), fail to check approve’s return value or verify that the external call consumed tokens, and do not revoke/reset allowances after external interactions. These patterns produce two distinct classes of exploitable outcomes depending on the token implementation and the external counterparty’s behavior: (1) tokens that revert when changing a non-zero allowance to another non-zero value (USDT-style) can cause operations to revert on subsequent calls (denial-of-service), and (2) if the spender does not fully consume the approved amount, the leftover allowance can be used later by a malicious or compromised spender to transferFrom(...) funds from the contract, enabling theft.

## Root cause

Assumptions about ERC‑20 semantics and inadequate handling of approvals:
- Unconditional approve(newAmount) without first setting allowance to 0 or using increaseAllowance/decreaseAllowance or permit.
- Not checking the return value of approve() (some tokens return false instead of reverting).
- Not verifying that the external call (e.g., deposit, transferFrom by a relayer, position manager) actually consumed the approved tokens (no balance-delta or allowance check).
- No cleanup/revocation of allowances after the external call completes.
These combined mistakes create both availability and authorization risks depending on token behavior and external counterparties.

## Impact

High (combined availability and theft risk):
- Denial-of-Service: For tokens that require zero-first allowance updates (e.g., USDT), calling approve(...) to change a non-zero allowance to another non-zero value will revert. Contracts that repeatedly call approve before interacting with external contracts (convertToV3, increaseLiquidity, _performSwap, relayToL1Burner) can become unusable for those tokens after a partial consumption leaves a residual allowance. This blocks legitimate operations until manual remediation.
- Theft/unauthorized transfer: When approve is granted to an externally-supplied target (e.g., staking target, relayer) and that target does not fully consume the allowance (or the token’s approve silently failed), the leftover allowance remains live. A malicious or compromised target (or any actor that can act as that spender) can later call transferFrom(contract, recipient, N) to drain approved tokens. In some flows the contract also clears internal state (e.g., queuedHashes) or emits events indicating success without verifying token movement, enabling an attacker to induce the contract to relinquish reattempt rights while retaining a live allowance.
- Silent failures and broken flows: For nonstandard tokens that return false from approve(), the function may proceed to call external services (relayer, staking target, position manager) believing an allowance exists when it does not, causing downstream failures or inconsistent state.
Overall, these issues can lead to stuck operations, loss of funds, or inconsistent bookkeeping depending on which contract and token are involved.

---

# getOwnerIncentives rejects valid ERC‑721 token IDs by assuming totalSupply() bounds IDs and enforcing strict increasing order (implicitly banning id==0)
****
- Severity: Low

## Targets
- getOwnerIncentives (Tokenomics)

## Description

The function enforces two unsafe invariants on caller-supplied unitIds before calling ownerOf: (1) each unitId must be <= IToken(registry).totalSupply(), and (2) unitIds must be strictly increasing per unitType via a zero-initialized lastIds array (unitId > lastIds[unitType]). Because totalSupply() is usually the minted count (not the maximum tokenId) and some registries may use non-sequential or 0-based ids, these pre-checks can incorrectly revert for otherwise-valid tokenIds. ownerOf is invoked only after these checks, so tokens that exist according to ownerOf but violate the numeric assumptions will be rejected with WrongUnitId (or OwnerOnly if owner mismatch).

## Root cause

Incorrect assumptions about ERC‑721 semantics combined with the ordering check: the code treats totalSupply() as an upper bound on valid tokenIds and uses a zero-initialized lastIds array to require unitId > lastIds, implicitly banning id == 0 and enforcing strict monotonicity. These numeric invariants are applied before querying the registry via ownerOf.

## Impact

Availability break for legitimate owners: valid unit owners may be unable to retrieve their incentives because getOwnerIncentives will revert on pre-checks even when ownerOf would succeed. Callers providing ids out-of-order, 0-based ids, or ids numerically greater than totalSupply (but still valid in the registry) will receive WrongUnitId and cannot proceed. This can break integrations, prevent claiming/querying incentives, and cause denial-of-service for incentive retrieval paths.

---

# Owner-controlled registry pointer allows reward theft and DoS by rebinding incentives to new registry addresses or non-conforming contracts
- Severity: Low

## Targets
- changeRegistries / accountOwnerIncentives / getOwnerIncentives (Tokenomics)
- changeRegistries (Tokenomics)
- changeRegistries (affects accountOwnerIncentives and getOwnerIncentives) (Tokenomics)

## Description

Tokenomics stores per-unit incentives keyed only by (unitType, unitId) while ownership/claim-time checks (ownerOf, totalSupply) are performed against mutable registry contract addresses (componentRegistry, agentRegistry). The owner can call changeRegistries to set these registry pointers to arbitrary non-zero addresses without migrating, rekeying, or otherwise rebinding existing mapUnitIncentives data. As a result, incentives that were accrued under a prior registry remain associated with the same numeric unitId but are validated against the newly-configured registry at claim time. If the new registry assigns those numeric IDs to attacker-controlled addresses (or the owner points a registry at a malicious contract), attackers can pass ownership checks and drain incentives. Similarly, pointing a registry to a non-conforming address (an EOA or a contract that does not implement the expected IToken ABI or reverts) will cause unguarded totalSupply()/ownerOf() calls to revert, blocking payout and view functions and effectively locking rewards.

## Root cause

Mismatched keying and unchecked, owner-controlled registry pointers: per-unit incentive state is keyed only by (unitType, unitId) and omits the registry address, while ownership verification is performed against the CURRENT registry contract address. changeRegistries allows the owner to replace registry addresses with arbitrary non-zero values and the contract invokes IToken functions (totalSupply, ownerOf) without runtime validation or defensive error handling. There is no migration, rekeying, nor interface compliance checks when a registry is swapped.

## Impact

High — two practical exploitation paths exist:

1) Theft/misallocation: if the owner (or an attacker who compromises the owner key) points a registry to a contract that mints or assigns the same numeric token IDs to attacker-controlled accounts (or points to a malicious registry implementation), those accounts will pass ownerOf checks and may claim incentives that were accrued for prior legitimate holders. This results in irreversible loss of funds for the original owners.

2) Denial-of-service / reward lock: if a registry is set to a non-token address (EOA) or a contract that reverts or returns malformed data for totalSupply()/ownerOf(), subsequent calls that iterate registries and invoke these functions will revert. That can block payout flows, view functions, and finalization logic, effectively locking rewards until the registry is corrected. Because changeRegistries accepts arbitrary non-zero addresses and the payout paths make unguarded typed external calls, accidental misconfiguration or malicious owner action is sufficient to cause this DoS.

---

# Neighborhood tick-selection logic allows invalid or non-maximal ranges — binary-search branch inversion and missing input validation produce incorrect lo/hi pairs

- Severity: Low

## Targets
- _raiseHigh (NeighborhoodScanner)
- pickHiMaxUtil (NeighborhoodScanner)

## Description

Two related logic defects in NeighborhoodScanner's range-selection code can cause returned (lo, hi) ranges to be incorrect: (1) _raiseHigh's binary-search inverts the branch that records feasible candidates, causing it to converge downward and often return non-feasible or non-maximal upper ticks instead of the highest feasible hi ≤ hiMax; and (2) pickHiMaxUtil accepts a caller-supplied lo without validating its relation to the current pool price and returns early from several branches (liquidity==0 and optimized-amount comparison shortcuts) without normalizing or running _neighborhoodSearch, which is the only helper that enforces the invariant TickMath.getSqrtRatioAtTick(lo) < sqrtP < TickMath.getSqrtRatioAtTick(hi). Together these bugs let the contract persist or return ranges that do not straddle the current price or fail to expand hi toward its intended maximum.

## Root cause

Two distinct implementation mistakes in the neighborhood-selection algorithm: (A) an inverted branch/recording condition in the binary-search implementation (_raiseHigh) that updates the answer on the wrong predicate outcome and thus searches in the wrong direction; (B) insufficient input validation and inconsistent control flow in pickHiMaxUtil — the function writes the caller-provided lo into state and takes multiple early-return paths that skip neighborhood normalization/_neighborhoodSearch, allowing invalid caller inputs to be returned directly.

## Impact

Medium. Functions that rely on neighborhood ranges will receive incorrect lo/hi pairs. Practical consequences include: - Incorrect liquidity range computations (over- or under-estimating concentrated liquidity) leading to mispriced or suboptimal position adjustments. - Downstream logic that assumes ranges straddle the current price may perform invalid operations (e.g., placing liquidity entirely on one side of the price), causing failed transactions, unexpected fees, or missed opportunities. - In contexts where range selection is security-sensitive, attackers or malicious callers could supply crafted lo values to influence returned ranges and extract economic advantage or disrupt higher-level strategies. This is primarily a correctness bug but can produce observable financial or operational impact depending on usage.

---

# DefaultTargetDispenserL2: bridging-decimals scaling omission and migrate paused-state inversion cause silent under-transfer and operational grief

- Severity: Low

## Targets
- syncWithheldAmount / getBridgingDecimals (DefaultTargetDispenserL2)
- syncWithheldAmount (DefaultTargetDispenserL2)
- migrate (DefaultTargetDispenserL2)

## Description

DefaultTargetDispenserL2 contains two distinct but high-impact implementation mistakes: (1) syncWithheldAmount / getBridgingDecimals assume bridgingDecimals <= 18 and implement only down-scaling, so when a derived contract (or the intended L1 token) uses >18 decimals the contract silently under-scales amounts sent to the bridge; and (2) migrate() contains an inverted paused-state check that permits migration only when the contract is paused (paused==2) rather than when active, forcing owners to pause before migrating. Together these defects produce silent, hard-to-detect fund under-transfer across the bridge and an unexpected, availability-impacting migration workflow.

## Root cause

Two implementation omissions/misassumptions: (A) asymmetric decimal handling — getBridgingDecimals() defaults to 18 in the base contract and syncWithheldAmount() only implements truncation for bridgingDecimals < 18; there is no branch to multiply/up-scale when bridgingDecimals > 18 and no guard requiring derived contracts to override the decimal value, so amounts intended for higher-precision destination tokens are silently reduced by 10^(bridgingDecimals-18). (B) logic inversion in migrate() — the pause-state test condition treats paused==1 (active) as an error and allows migration only when paused==2, i.e., when already paused, contrary to the intended policy.

## Impact

High for funds and operations. For bridging-decimals: recipients or contracts on the destination chain can receive values that are orders-of-magnitude too small (e.g., 20-decimal token expected but 18-decimal amount sent -> 100x under-transfer). This is silent (no revert) and leads to effective loss of user funds, persistent accounting mismatches, and operational confusion. For migration: the owner cannot perform migrations while the contract is active and must pause first, breaking intended workflows and potentially preventing timely migrations; this can force pausing in situations where pausing is undesirable or impossible, causing operational disruption.

---

# Oracle/TWAP integrity failures — math, state-ordering, unit-mismatches, and trust assumptions allow price manipulation and TWAP-guard bypass
****
- Severity: Qa

## Targets
- updatePrice (BalancerPriceOracle)
- validatePrice (UniswapPriceOracle)
- validatePrice (BalancerPriceOracle)
- getTwapFromOracle (LiquidityManagerCore)
- checkPoolAndGetCenterPrice (LiquidityManagerCore)

## Description

Multiple oracle- and price-validation-related functions across BalancerPriceOracle, UniswapPriceOracle, and LiquidityManagerCore contain a consistent set of defects that either compute TWAPs incorrectly, mutate oracle state before validation, mix incompatible numeric encodings, or trust unverified external inputs. These defects individually and in combination allow an attacker to (a) bias or poison stored averages, (b) make TWAP computations collapse to the current (manipulated) spot price, or (c) bypass TWAP-vs-spot deviation guards by forcing failure paths or by having oracle-returned values overwrite instantaneous readings. The result is that downstream systems depending on these oracles or guards (liquidity operations, slippage checks, buy/sell/fee operations, liquidations) can accept manipulated prices and suffer financial loss or incorrect behavior.

## Root cause

A family of implementation mistakes rather than a single bug: (1) incorrect TWAP arithmetic and ordering — cumulativePrice and averagePrice are updated and combined using invalid identities (double-counting elapsed time, adding stale averages instead of the current sample), (2) unit/representation mismatches — instantaneous prices (1e18-scale) are combined with Uniswap/Balancer cumulative encodings (UQ112x112 or cumulativePrice semantics) without conversion, (3) state mutation before validation — cumulativePrice is persisted before slippage checks and early returns leave storage in inconsistent states, and (4) trust/control-flow mistakes — unverified caller-supplied pool addresses, permissive handling of oracle/staticcall failures (fail-open), and variable overwrite/decoding errors cause the TWAP-vs-spot comparison to be skipped or trivially pass. These interacting root causes allow simple on-chain manipulations to produce persistent or immediate oracle corruption or to bypass safety checks.

## Impact

High. Practical, directly-exploitable outcomes include: 
- Oracle poisoning: attackers can inflate cumulativePrice or bias averagePrice so future TWAPs are corrupted and downstream pricing decisions (liquidations, collateral checks, trades) are wrong. 
- TWAP collapse to spot: algebraic/units errors or tautological computations make the TWAP equal the instantaneous manipulated price, removing protection against flash/MEV manipulation. 
- TWAP-guard bypass: forcing oracle observe() to revert, exploiting staticcall fail-open behavior, or supplying a malicious pool lets an attacker cause the contract to rely on instantaneous slot0 price (which can be manipulated within a block). 
- Overflow/DoS: mixing incompatible scales can overflow when multiplying price*elapsedTime or cause reverts in library calls (TickMath) if attacker-supplied cumulatives are out of bounds. 
Consequences: incorrect acceptance/rejection of prices, unauthorized trades/liquidity changes, mispriced fee/treasury operations, improper liquidations, and direct financial loss for users and the protocol.

---

# Unchecked token-position assumptions + global-balance accounting cause full-balance burns/transfers via collectFees
- Severity: Qa

## Targets
- _manageUtilityAmounts (LiquidityManagerCore)
- collectFees (LiquidityManagerCore)

## Description

collectFees() delegates post-fee handling to _manageUtilityAmounts(tokens, utilizationRate, true). Two interacting implementation mistakes cause catastrophic outcomes: (1) _manageUtilityAmounts assumes the protocol utility token (OLAS) appears exactly once in the provided tokens array and chooses olasAmount by positional logic (if tokens[0] == olas then amounts[0] else amounts[1]) without validating that either entry is OLAS; (2) _manageUtilityAmounts computes acted-on amounts from the contract's entire token balances (IToken(token).balanceOf(address(this))) and not from the specific newly-collected fee amounts. When collectFees calls _manageUtilityAmounts with utilizationRate == MAX_BPS (100%), the logic applies the operation against full contract balances. Combined, these defects allow normal collectFees calls to (a) burn the contract's entire OLAS holdings and (b) transfer the full balance of the paired token to the treasury, or otherwise revert/behave incorrectly if token arrays omit or reorder OLAS.

## Root cause

Two developer mistakes interacting: (A) positional assumption/missing validation — _manageUtilityAmounts uses tokens[0] == olas ? amounts[0] : amounts[1] and never checks that the tokens array actually contains OLAS exactly once (or at all); (B) incorrect data source for amounts — _manageUtilityAmounts reads the contract's total token balances as the amount to act on and caller collectFees passes utilizationRate == MAX_BPS, causing whole-balance operations rather than operations scoped to freshly-collected fees. The caller also ignores updatedBalances returned by _manageUtilityAmounts, hiding the misuse.

## Impact

High — direct, practical, and immediate loss of protocol funds and/or denial-of-service: - Full-balance OLAS burn: collectFees can irreversibly call _burn on the contract's entire OLAS balance, destroying protocol-held OLAS. - Full-balance transfer: the paired token's entire contract balance can be transferred to the treasury, moving far more than the intended fee amount. - Reverts/DoS: if the positional assumption misidentifies OLAS (array omits or reorders tokens), the function may attempt to burn/transfer an incorrect token amount and revert for insufficient balance, breaking caller flows. Because collectFees is an operational entrypoint, these outcomes can be triggered during normal use or by an attacker who can supply inputs that reach this call path, leading to catastrophic asset loss or availability failures.

---

# Hard-coded minimal output in Uniswap V3 swap allows accepting near-zero OLAS (massive slippage)
- Severity: Qa

## Targets
- _performSwap (BuyBackBurnerUniswap)

## Description

The Uniswap V3 swap path in _performSwap builds ExactInputSingleParams with amountOutMinimum set to 1 and calls exactInputSingle. This effectively disables any meaningful slippage protection: the router will accept the swap as long as at least 1 wei of OLAS is returned. The contract's V3 buy flow does not verify the returned olasAmount against an expected minimum (unlike the V2 flow which enforces oracle-based pre/post price checks). Because external callers can invoke the buyBack flow that forwards user-supplied token amounts and feeTier to the internal V3 swap, an attacker can create or manipulate conditions (low-liquidity pool, front-run/sandwich) so the swap consumes nearly the entire input token while returning negligible OLAS, and the transaction will not revert.

## Root cause

Two related implementation mistakes: (1) hard-coded amountOutMinimum = 1 in Uniswap V3 ExactInputSingle params (effectively no minimum output); and (2) missing post-swap numeric/assertion check of returned olasAmount or explicit slippage enforcement in the V3 path (unlike the V2 path which uses oracle pre/post price checks).

## Impact

An attacker (MEV bot or trader manipulating a low-liquidity pool) can force a buyBack via the V3 path to accept almost-zero OLAS in exchange for consuming a large amount of input token, causing the contract to lose nearly the entire input balance provided to the swap. Resulting OLAS transfer to bridge2Burner will be tiny/zero and funds will be effectively stolen/lost. This is a direct, on-chain fund loss vulnerability for buyBack callers or the contract's token balances.

---



# Positional OLAS assumption in _manageUtilityAmounts allows incorrect burn/transfer or revert

- Severity: Qa

## Targets
- _manageUtilityAmounts (LiquidityManagerCore)

## Description

The function assumes exactly one of tokens[0] or tokens[1] is the protocol token (olas) and uses the array positions to determine which balance to burn/transfer. It reads balances for tokens[0] and tokens[1] and then chooses olasAmount = amounts[0] if tokens[0] == olas, otherwise olasAmount = amounts[1]. There is no internal validation that either entry equals olas (or that olas appears exactly once). If callers supply a tokens array where neither entry is olas, the function will treat one of the non-OLAS token balances as olasAmount and attempt to burn/transfer that many OLAS. This leads to either a revert (if the contract lacks that many OLAS) or an incorrect burn/transfer of OLAS (if balances coincidentally match), causing incorrect treasury accounting or loss of protocol tokens.

## Root cause

Positional logic plus missing input validation: the function selects olasAmount by checking only tokens[0] == olas and otherwise assumes tokens[1] is OLAS. It never verifies that the tokens array actually contains olas exactly once (or at all) before using fixed positions.

## Impact

Depending on state and inputs, attackers or benign callers can cause:
- Immediate revert (denial of service) when an action that calls _manageUtilityAmounts fails because the contract is asked to burn/transfer more OLAS than it holds.
- Incorrect burning or transfer of OLAS to the treasury if the mistaken amount matches available OLAS, causing unintended loss of protocol tokens and corrupted accounting for utility/tax flows.
Overall severity: medium-high — financial loss or availability impact for treasury-related flows that call this function (collectFees, increaseLiquidity, decreaseLiquidity, changeRanges, convertToV3 when callers provide unchecked token arrays).

---

# Unprotected public initializers across contracts allow first-caller takeover and cascading protocol compromise

- Severity: Qa

## Targets
- initializeTokenomics (Tokenomics)
- initialize (LiquidityManagerCore)
- initialize (BuyBackBurner)
- initializeTokenomics & checkpoint (Tokenomics)
- refundFromBondProgram (Tokenomics)
- changeImplementation (LiquidityManagerCore)

## Description

Several contracts (Tokenomics, LiquidityManagerCore, BuyBackBurner and related implementations) leave owner unset at deployment (owner == address(0)) and expose external initialize/initializeTokenomics functions that set owner = msg.sender when owner == address(0). These initializers perform substantial privileged setup (assigning treasury/depository/dispenser/registries/implementation pointers, setting epoch/inflation parameters, or enabling owner-only operations) but lack any deployer/factory-only guard, initializer modifier, or constructor-set sentinel. As a result, the first external caller after deployment can permanently claim ownership and configure or corrupt critical addresses, parameters, and implementation pointers — enabling full administrative takeover, fund diversion, protocol misconfiguration, or DoS.

## Root cause

Missing protected-initializer pattern: constructors do not assign a trusted owner or sentinel, and public initializers rely solely on owner == address(0) to gate one-time setup. Initializers accept caller-supplied addresses/parameters and sometimes call virtual hooks after assigning owner. There is no restriction that the intended deployer/factory must call initialization, no initializer modifier (e.g., OpenZeppelin's Initializable), and no checks that prevent pre-launch or malicious parameter values.

## Impact

High. Practical, immediate exploits include: (1) first-caller becomes owner and can call owner-only setters to point treasury/depository/dispenser/registries to attacker-controlled addresses, redirecting or stealing funds; (2) attacker can change implementation pointers (via owner-only changeImplementation) to deploy malicious logic or hijack proxy behavior; (3) attacker-controlled initialization parameters can permanently corrupt tokenomics (inflationPerSecond, epoch counters, maxBond), causing under-minting or economic damage; (4) attacker-set depository can call privileged functions (e.g., refundFromBondProgram) to manipulate accounting; (5) initialization invoked before expected time can cause arithmetic issues (under-minting of year‑0 emissions) or enable checkpoint() to underflow and revert, causing DoS; (6) initializing code that calls virtual hooks after setting owner or reentrancy guards can allow overrides or delegatecalls to overwrite owner or break guards, enabling further exploitation. Consequences range from loss/diversion of funds and permanent misconfiguration to complete protocol compromise and denial of service.

---

# Public one-time initializers (initialize/initializeTokenomics) allow first-caller administrative takeover across multiple contracts

- Severity: Qa

## Targets
- initialize (BuyBackBurner)
- initialize (LiquidityManagerCore)
- initializeTokenomics (Tokenomics)
- changeImplementation (BuyBackBurner)

## Description

Multiple contracts (Tokenomics, LiquidityManagerCore, BuyBackBurner and related implementations) leave owner unset at deployment (owner == address(0)) and expose external one-time initializer functions that set owner = msg.sender when owner == address(0). These initializers perform privileged and irreversible setup (assigning owner, writing treasury/depository/dispenser/registry/implementation pointers, setting epoch/inflation parameters, or enabling owner-only operations) but lack constructor-set sentinels, initializer modifiers, factory-only guards, or any restriction on who may perform the initial call. As a result, an arbitrary account that calls the initializer before the intended deployer/factory can permanently claim ownership and configure or corrupt critical addresses, parameters, and implementation pointers.

## Root cause

Design and implementation omitted a protected-initializer pattern: constructors do not set a trusted owner or sentinel and initialization is deferred to public external functions that only check owner == address(0) before assigning owner = msg.sender. There are no initializer modifiers (e.g., OpenZeppelin Initializable/initializer), no deployer/factory-only checks, and initializers accept caller-supplied addresses/parameters (including pointers used later by proxies or protocol flows). Some initializers also call virtual hooks after assigning owner, increasing risk if overrides exist.

## Impact

High — immediate and practical full administrative takeover of any uninitialized instance. The first caller who invokes initialize/initializeTokenomics can become owner and then: set or replace core protocol addresses (treasury, depository, dispenser, registries, olas/ve), supply malicious parameter values (inflationPerSecond, epoch timing, maxBond, maxSlippage), call owner-only functions to transfer tokens or NFT positions, and change implementation pointers (via changeImplementation) to a malicious implementation. Consequences include theft or redirection of funds, permanent protocol misconfiguration, malicious upgrades leading to arbitrary code execution in proxies, denial of service (e.g., by corrupting epoch/timing state), and complete loss of control by legitimate operators.

---

# Unprotected public initializers, missing bootstrap events, and deferred constructor setup allow first-caller takeover and misconfiguration

- Severity: Qa

## Targets
- initializeTokenomics (Tokenomics)
- convertToV3 (LiquidityManagerCore)
- constructor (BuyBackBurner)

## Description

Multiple contracts defer critical setup to public external initializer functions (initialize / initializeTokenomics / _initialize) while leaving owner unset (address(0)) in the constructor. These initializers (Tokenomics.initializeTokenomics, LiquidityManagerCore.initialize, BuyBackBurner.initialize/_initialize) assign owner = msg.sender when owner == address(0) and perform privileged, irreversible configuration (owner assignment, pointers to treasury/depository/dispenser/registries/implementations, epoch/inflation parameters, swap/token/swap‑path configuration). Some initializer paths also write important observable state (e.g., donatorBlacklist) but fail to emit the corresponding events. Because there is no deployer/factory-only guard, no initializer modifier or sentinel set in the constructor, and initialization accepts caller-supplied addresses/parameters, any external account that calls these initializers first can permanently claim ownership and configure or corrupt critical protocol state without producing expected event logs.

## Root cause

Design and implementation omitted a protected-initializer/constructor bootstrap pattern. Constructors either do not set a trusted owner or defer essential setup to an external initialize flow. Initializers are public, only gated by owner == address(0), accept arbitrary parameters, and sometimes call virtual hooks. Additionally, some initialization code writes important state (e.g., donatorBlacklist) without emitting the corresponding events. There is no use of an initializer guard (e.g., OpenZeppelin Initializable), no factory-only restriction, and no verification that concrete _initialize implementations are invoked during deployment.

## Impact

High. Immediate exploitation by a first-caller enables full administrative takeover and/or misconfiguration across affected contracts: set owner and then call owner-only setters to point treasury/depository/dispenser/registries to attacker-controlled addresses; change implementation pointers to malicious logic; configure economic parameters (inflationPerSecond, epoch timing, maxBond, maxSlippage) to damage tokenomics; leave swap/token configuration unset causing runtime failures; and divert or permanently lock funds. Missing event emission (DonatorBlacklistUpdated) can desynchronize off‑chain tooling, causing incorrect UI/alerting behavior or missed security signals. Combined, these issues allow theft or redirection of funds, malicious upgrades, persistent protocol compromise, denial-of-service (e.g., by corrupting epoch/timing state or causing unchecked underflows/ reverts), and loss of observability for monitoring systems.

---



# Unchecked narrowing casts and truncation across Tokenomics → silent data corruption, invariant breaks, and long-term DoS
- Severity: Qa

## Targets
- changeStakingParams (Tokenomics)
- checkpoint (Tokenomics)
- checkpoint / updateInflationPerSecondAndFractions (Tokenomics)
- initializeTokenomics (Tokenomics)
- trackServiceDonations, checkpoint (Tokenomics)
- changeTokenomicsParameters (Tokenomics)
- _trackServiceDonations (Tokenomics)
- trackServiceDonations (Tokenomics)
- updateInflationPerSecondAndFractions (Tokenomics)

## Description

Multiple places in the Tokenomics contract perform unchecked narrowing casts (uint256 → smaller unsigned integer types) or perform validation after truncation. Solidity downcasts silently keep low-order bits rather than reverting, so values that exceed the target width are truncated. These truncations affect monetary/accounting fields (uint96), small counters/indices (uint8, uint16), timestamps and block numbers (uint32), and parameter staging logic. The net effect ranges from incorrect economic calculations and incentive misallocation to broken sequencing invariants and, in the extreme, permanent manager/Admin inability to update parameters after wrap-around.

## Root cause

Inconsistent and unsafe handling of width mismatches: the code narrows uint256 values to smaller storage types without (a) checking that inputs/results fit the narrower type, (b) validating the original uint256 inputs before truncating them, or (c) using saturation/safe-cast utilities. Additionally, some comparisons mix widths (e.g., comparing stored uint32 to block.number uint256) and some checks occur after truncation, allowing attacker-supplied out-of-range values to pass validation based on their low-order bits.

## Impact

High-severity and diverse impacts depending on site of truncation:   - Monetary/accounting corruption: truncating into uint96 (effectiveBond, maxBond, stakingIncentive, inflation-per-second slots, donation totals) can reduce or zero critical balances, break reward and bond issuance calculations, produce long-lived corrupted state, and enable economic manipulation by privileged actors.   - Parameter poisoning: casting-before-validation lets out-of-range owner/manager inputs be truncated and staged/applied, allowing unintended parameter changes or preventing certain valid values (off-by-one validation).   - Sequencing/logic invariant breaks: truncation of block numbers (uint32) defeats same-block donation checkpoint guards, enabling donation+checkpoint within the same block.   - Time/epoch corruption and long-term DoS: downcasting timestamps (uint32) or year counters (uint8) truncates or wraps time/year indices; once wrapped, manager update functions that compare wide numYears to the narrowed stored year will revert, permanently preventing admin updates.   - Rounding and allocation loss: integer division and unchecked casts in donation handling can drop remainders and silently lose tokens or misallocate per-unit rewards.   Many of these issues are exploitable by privileged roles (owner/treasury/manager/depository) or by supplying crafted inputs; some are latent but catastrophic when activated (year/timestamp wrap after decades), while others can be triggered immediately by misconfiguration or a compromised privileged key.

---

# Unchecked divisors and missing input validation across contracts leading to DoS and incorrect results
- Severity: Qa

## Targets
- _finalizeIncentivesForUnitId (Tokenomics)
- validatePrice (BalancerPriceOracle)
- pickHiMaxUtil (NeighborhoodScanner)
- pickLoMaxUtil (NeighborhoodScanner)
- getPrice (UniswapPriceOracle)

## Description

Multiple contracts contain unchecked divisions or assume caller/external state invariants (non-zero divisors, positive spacing, non-zero reserves, non-zero stored averages) without validating them. These assumptions lead to two broad, high-impact classes of failures: (1) runtime panics / division-by-zero reverts that cause denial-of-service of public API flows, and (2) fragile / incorrect arithmetic (algebraic mistakes, truncation, overflow) that returns wrong economic values (e.g., degenerate TWAPs) and can be manipulated or relied on incorrectly by downstream logic.

## Root cause

Developers rely on implicit invariants about inputs and external state rather than enforcing them at public/external entry points and right before arithmetic that uses them as divisors or loop strides. Specifically: no require/guard that denominators (averagePrice, selected reserve, sumUnitTopUpsOLAS) are non‑zero; no require that tickSpacing > 0; and a flawed algebraic reconstruction of TWAP that cancels fresh price information and uses integer division (C / A) to infer time. Multiplications that can overflow are not defended, and many helper routines perform modulo/division with unvalidated spacing.

## Impact

High — combined availability and correctness issues across the protocol:
- Denial of service: unguarded divisions cause immediate reverts when denominators are zero (finalize incentives, validatePrice, getPrice, scanner pick* functions). Because reverts often bubble up, attackers or benign states can block public flows (claims, price validation, scanner queries) and cause repeated transaction failures.
- Gas exhaustion / DoS: accepting negative or zero tickSpacing causes loop strides and binary-search updates to invert or become zero, producing non-terminating or out-of-gas executions (NeighborhoodScanner pickHiMaxUtil/pickLoMaxUtil).
- Incorrect economics / oracle poisoning: validatePrice’s TWAP reconstruction algebraically collapses into the stale stored averagePrice (ignoring current on-chain price) or suffers from truncation/overflow, allowing attackers or stale state to cause incorrect validation decisions that accept out-of-market prices or reject valid ones.
- Locked funds / unclaimable incentives: division-by-zero in incentive finalization can leave incentives forever unclaimable for affected units/epochs until unrelated state changes, effectively locking value.
- Low exploitation complexity: many issues are exploitable by providing crafted inputs (tickSpacing = 0 or negative) or by manipulating external state (draining a reserve to zero) — both low technical bar for a skilled adversary.
- Downstream impact: callers or off-chain tooling that assume these functions are safe/always-return will fail, potentially cascading into larger operational outages.

---

# Integer truncation / asymmetric rounding causes loss of value and broken invariants
- Severity: Qa

## Targets
- _trackServiceDonations (Tokenomics)
- optimizeLiquidityAmounts (NeighborhoodScanner)

## Description

Multiple components perform arithmetic using integer division or floor-only multiplicative formulas without accounting for remainders or providing compensating rounding. In Tokenomics._trackServiceDonations, per-unit shares are computed with amounts[i] / numServiceUnits and any remainder (amounts[i] % numServiceUnits) is dropped and never recorded, so donated tokens can be irrecoverably lost. In NeighborhoodScanner.optimizeLiquidityAmounts the conversion liquidity → amounts → liquidity uses floor-truncating formulas in LiquidityAmounts; producing amountsDesired via floor arithmetic can make the round-trip produce less liquidity (often by 1), breaking the expectation that amountsDesired reproduces the computed liquidity.

## Root cause

Use of integer arithmetic that truncates toward zero (floor behavior) in critical value-distribution and conversion codepaths, combined with no mechanism to record, redistribute or compensate for remainders. The code assumes (explicitly or implicitly) that the forward and inverse conversions or splits are exact in integer space, but they are not. There is no residual accumulator, deterministic rounding policy (e.g., distributing remainders across units), or upward rounding/ceil where needed to preserve conserved quantities.

## Impact

Tokens and value can be silently lost or mis-accounted for, breaking invariants and producing user-visible mismatches: (1) Donations split across many units can be partially or entirely discarded (if amounts[i] < numServiceUnits the entire donation can become zero), causing underpayment of rewards and theft of donor value. (2) Liquidity calculations may return amounts that, when supplied, yield strictly less liquidity than expected (commonly off by 1 liquidity unit), leading to UI inconsistencies, failed on-chain checks or invariant violations, and small unexpected losses or misallocations. While not always catastrophic, these bugs can cause financial loss, accounting drift, failed assertions, and reputational damage.

---

# Missing input validation in getV3Pool — out-of-bounds indexing of tokens array
- Severity: Qa

## Targets
- getV3Pool (BuyBackBurnerUniswap)

## Description

getV3Pool indexes tokens[0] and tokens[1] unconditionally and forwards them to IFactory.getPool. The function checks only that feeTier is non-negative; it does not check tokens.length, nor does it validate that the two token addresses are non-zero or distinct. If callers provide an array with fewer than two elements the function will perform an out-of-bounds access and revert (panic). Extra elements are silently ignored and the contract does not enforce that the array contains exactly two addresses.

## Root cause

Missing input validation: the implementation assumes callers always pass an address[] of length >= 2 with valid, distinct token addresses. There is no require/guard to check tokens.length or address validity before indexing.

## Impact

A caller (external or internal) supplying an empty or single-element tokens array will cause a panic (OOB array access) and revert execution, resulting in denial-of-service for that call path. Because the function is public any external actor or other contract that forwards unvalidated input can trigger the revert. Even if the downstream factory would safely return address(0) for invalid token pairs, the panic occurs before the external call and cannot be mitigated by the factory behavior. Additionally, silently accepting arrays with extra elements or identical/zero addresses can lead to logic mismatches or incorrect pool lookups.

---

# Uses Vault getPoolTokens balances as if they were exitPool output — returned per-token amounts can be stale/wrong
****
- Severity: Qa

## Targets
- _checkTokensAndRemoveLiquidityV2 (LiquidityManagerOptimism)

## Description

The function _checkTokensAndRemoveLiquidityV2 reads token addresses and raw Vault-held balances via IBalancerV2.getPoolTokens(v2Pool) into an amounts array, then calls IBalancerV2.exitPool to withdraw liquidity but never updates or re-measures amounts afterward. Because exitPool does not populate caller memory with per-token exit amounts (and does not return them), the amounts array left in memory continues to reflect the Vault's reported pool balances at the time of getPoolTokens, not the actual token quantities received by this contract from exitPool. Any downstream logic that consumes and trusts that returned array (for accounting, bridging, transfers, or distribution) will therefore operate on incorrect numbers.

## Root cause

Misunderstanding and misuse of the Balancer Vault API: the implementation assumes getPoolTokens' returned balances correspond to the actual per-token amounts withdrawn by exitPool and assumes exitPool will populate or update caller memory with exit amounts. The code never measures token balances after exitPool (e.g., by checking token.balanceOf(address(this)) or capturing exit return values where available) nor recomputes per-token outputs based on Vault receipts.

## Impact

Medium–High: Downstream accounting, distribution, or bridging code can over-credit or under-credit recipients, mis-route funds, or perform incorrect transfers based on the stale amounts array. This can cause reconciliation discrepancies, failed cross-chain operations, incorrect bookkeeping, and potential financial loss or inconsistent protocol state. The issue is not an immediate direct theft of funds by this misread alone, but it can lead to incorrect token movements and enable operational mistakes with financial consequences.

---



# Tokenomics epoch getters return default/incorrect data due to sparse initialization and off-by-one epoch indexing
****
- Severity: Qa

## Targets
- getUnitPoint (Tokenomics)
- getLastIDF (Tokenomics)
- getEpochEndTime (Tokenomics)

## Description

Several public getters in Tokenomics (getUnitPoint, getLastIDF, getEpochEndTime) return values that can be default (zero) or point at the wrong epoch because the contract uses a sparse initialization pattern for epochs and applies incorrect epochCounter semantics. Callers can therefore receive misleading zeroed structs/timestamps or the IDF for the upcoming epoch rather than the last settled epoch. These problems arise because getters do not validate that the requested epoch has been initialized and one getter (getLastIDF) reads the wrong epoch slot due to an off-by-one interpretation of epochCounter.

## Root cause

1) Sparse/partial initialization of mapEpochTokenomics combined with public getters that return raw stored values without existence checks: mappings in Solidity return zeroed defaults for unwritten keys, and getUnitPoint/getEpochEndTime do not verify an epoch was initialized before returning data. 2) Incorrect use of epochCounter: checkpoint() stores settled data into mapEpochTokenomics[eCounter + 1] and then advances epochCounter = eCounter + 1, but getLastIDF() reads mapEpochTokenomics[epochCounter] expecting the last settled epoch. This off-by-one mismatch makes getLastIDF return the upcoming/current epoch's IDF instead of the last settled one.

## Impact

Medium — callers (on-chain contracts, off-chain services, and frontends) can be misled by zero/empty UnitPoint structs or zero endTime timestamps for uninitialized epochs, and by receiving an IDF from the wrong epoch. Resulting consequences include incorrect reward calculations, wrong eligibility or time-based checks, misreported metrics, broken UI/UX (e.g., showing epoch end as Unix epoch 0), and downstream logic using stale or incorrect economic parameters. While not an immediate direct theft vector, these integrity/availability failures can create incorrect incentive distributions, reconciliation errors, and enable misuse or exploitation where economic logic depends on accurate epoch data.

---



# Unchecked ERC‑20 interactions (transfer/approve) across contracts cause silent failures, misrouting, stuck funds, and reentrancy risk
****
- Severity: Qa

## Targets
- _manageUtilityAmounts (LiquidityManagerCore)
- _burn (LiquidityManagerOptimism)
- buyBack (BuyBackBurner)
- transfer (BuyBackBurner)
- _performSwap (BuyBackBurnerUniswap)

## Description

Multiple contracts assume standard ERC‑20 behavior (transfer/approve always succeed or revert) and perform unchecked external calls (IERC20.transfer, IToken.transfer, IERC20.approve) or rely on abstract hooks that affect token movement. These unchecked calls and assumptions cause silent transfer/approve failures (tokens remain in contract), misreported events, incorrect accounting, possible misrouting of swapped tokens, and exposure to fee‑on‑transfer or malicious token behavior (including reentrancy). Affected code paths include LiquidityManagerCore._manageUtilityAmounts, LiquidityManagerOptimism._burn, BuyBackBurner.buyBack/_buyOLAS/transfer, BuyBackBurner.transfer, and BuyBackBurnerUniswap._performSwap.

## Root cause

The contracts perform external ERC‑20 interactions without verifying outcomes and make unsafe assumptions about token semantics and derived implementations. Specific root causes observed across the codebase:
- Calling IERC20.transfer or IToken.transfer without checking the returned bool (no require or SafeERC20/SafeTransferLib wrapper).
- Calling IERC20.approve without validating its returned bool or handling non‑standard approve behavior.
- Not verifying post-transfer recipient balances (no delta checks) so fee‑on‑transfer/deflationary tokens are misaccounted.
- Relying on abstract/internal virtual hooks (e.g., _burn, _performSwap) without validating behavior or pre/post state, allowing misrouting or no‑op implementations.
- Assuming callers provide well-formed token arrays (e.g., tokens[1] == olas) without validation.
- Lacking reentrancy protection and access control on external-transfer helper functions.

## Impact

Realistic and material consequences include:
- Silent failed transfers: Non‑standard ERC‑20s that return false on transfer/approve will cause the contract to continue execution while tokens were not moved — treasury, bridge, or burner recipients receive nothing despite events indicating success.
- Stuck funds and incorrect accounting: Tokens stuck in contracts cause auditing mismatches and may be irrecoverable if no alternative withdrawal exists.
- Misrouted or lost swap proceeds: buyBack trusts an abstract swap to deposit OLAS to the contract, then forwards the entire balance; a malicious/buggy _performSwap can route proceeds elsewhere or consume contract balance, causing loss.
- Fee-on‑transfer / deflationary tokens: recipients receive less than emitted TokenTransferred amounts, breaking accounting and downstream logic.
- Reentrancy and malicious token execution: unchecked transfer calls to tokens with arbitrary code can trigger reentrancy or unexpected side effects because there is no reentrancy guard and some transfer functions are externally callable.
- State invariant violations: callers that expect revert semantics to roll back state (e.g., _locked flag in LiquidityManagerCore) can have invariants broken when a transfer silently fails, leading to inconsistent contract state.
- Operational disruption: swap/approve failures can cause DoS of swapping functions and require manual recovery or upgrades.
Overall severity: high — these issues can lead to loss of funds, broken protocol accounting, and exploitable behaviors when interacting with non‑standard or malicious tokens or with misconfigured derived implementations.

---

# Inconsistent event emission and stale event context leading to off-chain observability errors
****
- Severity: Qa

## Targets
- initializeTokenomics (Tokenomics)
- reserveAmountForBondProgram / refundFromBondProgram (Tokenomics)
- initialize (LiquidityManagerCore)

## Description

Multiple functions across the codebase either omit emitting canonical events when state is first initialized or emit events that reference stale contextual data. Specifically: (1) Tokenomics.initializeTokenomics writes manager addresses (treasury, depository, dispenser) to storage but does not emit the corresponding TreasuryUpdated/DepositoryUpdated/DispenserUpdated events; (2) LiquidityManagerCore.initialize sets maxSlippage but does not emit MaxSlippageUpdated for the initial assignment; and (3) Tokenomics.reserveAmountForBondProgram and refundFromBondProgram emit EffectiveBondUpdated(epochCounter, eBond) without advancing or recomputing epochCounter, causing the event to reference a stale epoch when checkpoint() has not yet been called. In each case the on-chain state is set correctly, but the emitted event stream (which many off-chain systems rely on) is inconsistent or incorrect.

## Root cause

Inconsistent eventing policy and assumptions about when contextual state (like epochCounter) is advanced. Initializers and some state-mutating functions do not follow the same event-emission behavior as their updater counterparts, and some emit events using stored context that may be stale because the code path that advances that context (checkpoint) is not invoked prior to emitting.

## Impact

Low-to-medium operational risk: off-chain consumers (indexers, UIs, analytics, monitoring, and automation) that rely on events to discover initial configuration or to attribute updates to the correct epoch can be misled. Consequences include incorrect UI displays, missed or false alerts, inaccurate historical reconstruction, misapplied automation (e.g., bots acting on assumed defaults), and audit/forensic confusion. The on-chain state remains correct; these issues do not directly enable on-chain fund loss or privilege escalation, but they can lead to operational incidents and loss of trust in off-chain tooling.

---

# Assuming standard ERC‑20 semantics / trusting external actors without post-transfer verification (misstated events, failed migrations, and potential loss/diversion of tokens)
****
- Severity: Qa

## Targets
- transferToken (LiquidityManagerCore)
- migrate (DefaultTargetDispenserL2)
- relayToL1Burner (Bridge2BurnerGnosis)
- relayToL1Burner (Bridge2BurnerOptimism)

## Description

Multiple contracts assume that an ERC‑20 transfer/transferFrom call (or an external relayer/bridge) will (a) not revert, (b) return/behave according to the canonical bool-returning ERC‑20 ABI, and (c) deliver the full requested token amount to the intended recipient. The codebase uses high-level typed transfers (IToken.transfer) or SafeTransferLib which only checks call success/return value, and then immediately (1) emits events that report the requested amount, (2) advances protocol state based on that assumption, or (3) trusts a relayer/bridge to forward the exact approved amount — without any post-call verification of recipient balances, allowance consumption, or returned data. These assumptions break for common token deviations (non‑standard ERC‑20s that omit a bool return, fee-on-transfer/reflection/burn tokens, malicious or buggy relayers), producing misleading events, stuck funds, failed migrations, or diverted/stolen tokens.

## Root cause

The contracts conflate 'call succeeded' with 'full amount received by recipient' and rely on typed ERC‑20 interfaces (or SafeTransferLib's basic call checks) rather than performing low-level tolerant calls and verifying post-transfer state (recipient balance delta, allowance consumption, or expected events). They also assume trusted behavior from external relayers/bridges without defensive post-call checks.

## Impact

- Misleading on‑chain observability: TokenTransferred events report the requested amount rather than the actual amount received, causing inaccurate dashboards, analytics, or off‑chain accounting.
- Migration failures or locked funds: migrate can revert on non‑standard ERC‑20s (no bool return) leaving tokens stuck, or succeed but transfer less than the contract's balance if the token is fee‑on‑transfer.
- Broken burn semantics and potential theft/diversion: relay/withdraw flows that approve relayers and assume they will forward the full amount can result in the burn address receiving less or none of the intended tokens if the relayer is buggy/malicious or if the token deducts fees. Approvals/relayer interactions combined with _getBalance() reverts for small balances can also leave funds stuck.
- Protocol/accounting integrity loss: financial invariants (e.g., 'all OLAS held were migrated' or 'X tokens burned') can be violated, leading to incorrect protocol state, user losses, or economic inconsistencies.
- These are not classic reentrancy exploits, but can lead to material loss or operational failure depending on token behavior or relayer trustworthiness.

---

# Unsafe external token/staking interactions: missing post-call verification, unsafe approve-before-call, and reentrancy/ordering issues
****
- Severity: Qa

## Targets
- redeem (DefaultTargetDispenserL2)
- transfer (BuyBackBurner)

## Description

Several functions make unchecked external calls to token or staking contracts and assume standard ERC-20 semantics (no fees, no callbacks, truthful return values). They: (1) approve a target immediately before calling an external deposit, (2) perform token transfers or external calls before finalizing local state or verifying outcomes, and (3) do not use SafeERC20 nor check transfer return values. These patterns allow malicious or nonstandard tokens/staking targets to avoid transferring tokens while causing state changes, manipulate balances via callbacks, reenter the contract, or cause event/logging to diverge from actual on-chain transfers.

## Root cause

The contracts violate checks-effects-interactions and make optimistic assumptions about external contracts and token implementations. They (a) trust external staking contracts to pull/receive tokens without performing post-call balance verification, (b) call approve immediately before an external call which can trigger token hooks/callbacks or reentrancy, and (c) perform external transfers/calls before storing/logging final local state and without using SafeERC20 or checking boolean returns.

## Impact

- Logical accounting breaks: queued deposits or state entries can be marked completed while no tokens were actually transferred, enabling effective double-crediting or inconsistent bookkeeping.
- Event/log mismatch: emitted events may report recipients or amounts that differ from what was actually transferred (notably with fee-on-transfer tokens), causing incorrect on-chain records and breaking off-chain monitoring or accounting.
- Reentrancy and state-manipulation: malicious or nonstandard token/staking contracts can reenter during approve/transfer/deposit calls to mutate contract state, potentially causing incorrect behavior or enabling exploitation.
- Silent failures: without SafeERC20/return checks, nonstandard ERC-20s that return false instead of reverting can cause transfers to fail silently while the contract proceeds.
- Denial-of-service or fund loss: inconsistencies can lead to lost funds, incorrect emissions, failed incentives, or denial of correct deposits/bequests.