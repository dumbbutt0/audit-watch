# P285 — INLINE_GUARD_AUDIT

Manual audit (full data in `outputs/audit.json`): claim_many + the newly-READY set + still-refuted anchors + the
VALUE/RECIPIENT/UNKNOWN reclassifications + L2Governor + V3Vault. Per item: token context correct? does the guard really
gate execution? does the read really feed value/recipient? status correct? any false unblock / false block / hallucinated
source context?

## claim_many (READY) — the unblock
`address _nftOwner = IVotingEscrow(_voting_escrow).ownerOf(_tokenId);` then the reward is sent to `_nftOwner`. The only
`ownerOf(` occurrence is this assignment → **RECIPIENT_READ**, not in any require/assert/if-revert/modifier gate.
Correct: it is the buggy recipient (the sibling `claim` uses `getOriginalOwner`). Lifts via P282 in-span anomaly + P284
SIBLING_REFERENCE_FOUND HIGH; core dims HIGH/HIGH/MEDIUM; specific PoC assertion. **No hallucinated context.** This is the
documented Blackhole M-04 shape. ✔ correct unblock.

## Still-refuted (true guards held) — audited
- **V3Vault.transform**: `if (loanOwner != msg.sender && !transformApprovals[loanOwner][tokenId][msg.sender]) { revert
  Unauthorized(); }` → loanOwner / msg.sender / transformApprovals all EXECUTION_GUARD (if-revert). ✔ correct block.
- **VotingEscrow.withdraw**: `assert(_isApprovedOrOwner(msg.sender, _tokenId));` → EXECUTION_GUARD (assert). This was the
  one true guard the first implementation MISSED (assert not covered); fixed by adding `assert` to gate detection. ✔.
- 5 `require(...)`/`if-revert`/modifier unit fixtures → EXECUTION_GUARD. ✔.

## Reclassified-but-held (no false READY) — audited
- **CollateralTracker.withdraw / redeem**, **V3Vault._withdraw**: `if (msg.sender != owner) { allowance -= shares }` /
  `{ _spendAllowance(...) }` — the ERC4626 withdraw-on-behalf pattern; the if-block has **no revert**, so it is not a
  hard access gate (the allowance helper gates internally). Classified UNKNOWN_READ → held at NEEDS_VALUE_FLOW /
  NEEDS_STATE_MACHINE. The prior INLINE_GUARD_REFUTED was over-conservative; the new status is held (not READY). ✔.
- **LibConvert._withdrawTokens / FieldFacet._harvest**: `LibTractor._user()` is a current-user READ → VALUE_READ →
  held. ✔.
- **SubnetActorActivityFacet.batchSubnetClaim**: `whenNotPaused` is a LIVENESS control (does not restrict the caller) →
  VALUE_READ → held. Acceptable (see LIMITATIONS). ✔.

## L2Governor.execute / IBeanstalk
L2Governor → READY via D2 state-machine (unaffected by D1; PoC 2/2 PASS). IBeanstalk.cancelPodListing → NEEDS_SOURCE_SPAN
(declaration-only). ✔ unchanged.

## Tally
newly READY = 1 (claim_many, correct) · false unblock = 0 · false block = 0 · hallucinated source context = 0 ·
severe FP = 0. The one true-guard gap (assert) was found here and fixed before finalizing.
