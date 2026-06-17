# Audit Submission Pack

## Executive Summary

- **0** High/Critical findings
- **0** Medium findings
- **0** Low findings
- **0** compound risk pairs identified
- **5** findings require PoC before submission

## Submit-Ready Findings

## [1] ZETA-04 — onReceive lacks whenNotPaused (pause does not halt inbound delivery); onRevert has it

**Severity:** Medium  
**Score:** ?/35  |  **Confidence:** ?/5

**Location:** contracts/evm/ZetaConnector.eth.sol → `onReceive()`

### Description

onReceive is onlyTssAddress but NOT whenNotPaused, while onRevert IS whenNotPaused. Emergency pause cannot stop inbound token delivery/callbacks.

### Proof of Concept

see L3 readiness record / harness (if built)

### Recommendation

see triage

---
## [2] ZETA-12 — Swap deadline computed as block.timestamp+MAX_DEADLINE(200s); Trident path has no deadline (weak MEV protection)

**Severity:** Medium  
**Score:** ?/35  |  **Confidence:** ?/5

**Location:** contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol → `get*Zeta*/get*From*()`

### Description

deadline = block.timestamp + 200 is always satisfied at inclusion time, so it provides no staleness protection; Trident router params omit a deadline entirely. minAmountOut is the only slippage guard and depends on the caller.

### Proof of Concept

see L3 readiness record / harness (if built)

### Recommendation

see triage

---

## Findings Requiring PoC

## [3] ZETA-01 — ERC20Custody.withdraw transfers exact amount, ignoring fee-on-transfer tokens (custody insolvency)

**Severity:** Medium  
**Score:** ?/35  |  **Confidence:** ?/5
**Status:** PoC required before submission

**Location:** contracts/evm/ERC20Custody.sol → `withdraw()`

### Description

withdraw() does IERC20(asset).safeTransfer(recipient, amount) with the deposit-credited amount; deposit() uses a balance-delta but withdraw() does not, so for a fee-on-transfer whitelisted asset the contract pays out more than it net-received.

### Proof of Concept

see L3 readiness record / harness (if built)

### Recommendation

see triage

---
## [4] ZETA-05 — No internalSendHash replay/dedup tracking in connectors (double-delivery if TSS replays)

**Severity:** Medium  
**Score:** ?/35  |  **Confidence:** ?/5
**Status:** PoC required before submission

**Location:** contracts/evm/ZetaConnector.eth.sol → `onReceive/onRevert()`

### Description

No mapping(bytes32=>bool) of processed internalSendHash; the same hash can be processed repeatedly. internalSendHash is only used in events / passed to mint() for tracing.

### Proof of Concept

see L3 readiness record / harness (if built)

### Recommendation

see triage

---
## [5] ZETA-06 — Uninitialized interactorsByChainId[chain] (empty bytes) lets empty zetaTxSenderAddress pass sender check

**Severity:** Medium  
**Score:** ?/35  |  **Confidence:** ?/5
**Status:** PoC required before submission

**Location:** contracts/evm/tools/ZetaInteractor.sol → `isValidMessageCall()`

### Description

modifier compares keccak256(sender) vs keccak256(interactorsByChainId[srcChain]) without first asserting the interactor entry is set; both empty -> keccak256('')==keccak256('') passes. _isValidChainId(ZERO_BYTES) guard exists but is NOT used in the modifier.

### Proof of Concept

see L3 readiness record / harness (if built)

### Recommendation

see triage

---
## [6] ZETA-10 — getEthFromZeta lacks nonReentrant while sending ETH to caller-controlled destinationAddress (cross-fn reentrancy)

**Severity:** High  
**Score:** ?/35  |  **Confidence:** ?/5
**Status:** PoC required before submission

**Location:** contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol → `getEthFromZeta()`

### Description

getEthFromZeta swaps ZETA->WETH->ETH then destinationAddress.call{value}('') with NO nonReentrant (getTokenFromZeta has it). Re-entry into unguarded getZetaFromEth/getZetaFromToken is possible during the ETH callback. Same pattern in PancakeV3.

### Proof of Concept

see L3 readiness record / harness (if built)

### Recommendation

see triage

---
## [7] ZETA-11 — Trident strategy uses poolFactory.getPools(...)[0] with no length/zero/legitimacy validation

**Severity:** Medium  
**Score:** ?/35  |  **Confidence:** ?/5
**Status:** PoC required before submission

**Location:** contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol → `getZetaFromEth/getZetaFromToken/getEthFromZeta()`

### Description

pairPools[0] used directly as the swap pool with no check that the array is non-empty or the pool is canonical; a front-run/permissionless factory entry could route swaps through an attacker pool, and an empty array reverts (DoS).

### Proof of Concept

see L3 readiness record / harness (if built)

### Recommendation

see triage

---

## Appendix — Downgraded Findings

These findings were downgraded during triage and are not recommended for submission.

- **ZETA-02** (Low): 
  - Reason: zetaFee transfer not balance-checked is an accounting-drift only and only if `zeta` itself is fee-on-transfer; no external theft. C=Medium (< High). Does not meet ICE advance bar.
- **ZETA-03** (Low): 
  - Reason: Trust-root rotation lacks timelock/two-step; impact requires a compromised PRIVILEGED key (TSS/updater/FUNGIBLE_MODULE). Centralization/admin-trust class — exploitability Privileged, not permissionless. Routed downgraded to surface the L3 privileged path.
- **ZETA-07** (Low): 
  - Reason: Zero gas fee only when FUNGIBLE_MODULE sets GAS_LIMIT=0 (privileged misconfig). Fee-leakage, not theft. Below ICE advance bar.
- **ZETA-08** (Low): 
  - Reason: Mint authority via mutable SYSTEM_CONTRACT_ADDRESS w/o zero-guard is centralization (requires FUNGIBLE_MODULE compromise). Privileged exploitability; QA-level zero-address hardening.
