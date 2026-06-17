# P290 — POC_INTENT_FREEZE (pre-reveal; frozen BEFORE any PoC code)

One READY candidate (not lens-driven). Frozen hypothesis = the pipeline's pre-reveal claim; the PoC tests it. Findings
SEALED.

## Candidate: Pools.deposit (EXTERNAL_INTEGRATION; P279 template, invariant_delta NO_REFERENCE)
- **candidate_id**: coverage_manifest:Pools:deposit:13
- **contract/function**: Pools.deposit(IERC20 token, uint256 amount) external nonReentrant
- **mechanism hypothesis (pipeline, P279 EXTERNAL_INTEGRATION template)**: a crafted external/callback response on the
  integration path leaves Pools state inconsistent or value misrouted.
- **source basis**: `_userDeposits[msg.sender][token] += amount; token.safeTransferFrom(msg.sender, address(this),
  amount);` under `nonReentrant`; comment notes only fee-less tokens should be whitelisted.
- **attacker path (claimed)**: attacker supplies a token whose transferFrom callback re-enters Pools to corrupt state.
- **impact delta (claimed)**: inconsistent `_userDeposits` / pool accounting.
- **victim/gainer**: pool / other depositors vs attacker.
- **invariant**: deposit accounting must be consistent across the external token call.
- **assertion (PoC)**: a malicious-callback token re-entering `deposit` corrupts state.
- **control/refutation**: `nonReentrant` blocks re-entry and `safeTransferFrom` is a standard pull with no DEX callback →
  the claimed callback mechanism is expected to be **REFUTED**. (Note: the source comment hints the real risk is
  fee-on-transfer accounting — a DIFFERENT mechanism the pipeline did NOT derive; not retrofitted here.)
- **recommended tier**: C (faithful reproduction of the nonReentrant deposit + a malicious-callback token).

## Honest note (pre-reveal)
This READY is NOT P289-lens-driven and NOT source-faithful: `deposit` is `nonReentrant` with a plain `safeTransferFrom`
and no external callback. The frozen P279 EXTERNAL_INTEGRATION template lifted it on the class label + a generic
hypothesis. The PoC is expected to refute the claimed callback mechanism (→ PRE_REVEAL_READY_UNSUPPORTED).
