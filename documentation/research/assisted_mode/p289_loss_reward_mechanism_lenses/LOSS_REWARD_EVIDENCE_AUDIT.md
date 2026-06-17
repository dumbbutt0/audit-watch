# P289 — LOSS_REWARD_EVIDENCE_AUDIT

Manual audit: the newly-READY candidate, the ECG High exact-loci, the held lens-match, and the 3 regressions.

## NEWLY READY — SurplusGuildMinter.stake (loss_on_stake → LOSS_ON_STAKE_FOUND, MEDIUM)
- **Lens match real?** Yes. Source: `require(lastGaugeLoss != block.timestamp, "loss in block")` guards ONLY a
  same-block loss; the function records `lastGaugeLoss`/`profitIndex` into the new `_stakes[msg.sender][term]` and pulls
  CREDIT + mints GUILD. A PRIOR-block gauge loss (lastGaugeLoss < block.timestamp) passes the guard yet still applies to
  the new stake → the staker is slashed for a pre-existing loss.
- **Source spans sufficient?** Yes — stake verb + loss term (`lastGaugeLoss`) + per-user write (`_stakes[`) + the
  same-block-only guard, all in-span.
- **Attacker path valid?** Yes — permissionless `stake` after a prior-block loss exists in the gauge.
- **Invariant specific?** Yes — a new stake must exclude prior-block loss (not only same-block). **Assertion
  implementable?** Yes (seed prior loss → stake → assert slash vs initialized-control).
- **ECG-specific hard-coding?** None — signals are generic (stake/loss/index/user-write/same-block-guard regex). A
  renamed function with the same shape matches (test enforced).
- **Status correct?** Yes. This is the documented awarded **H-04** mechanism → STRONG match. **No over-claim.**

## ECG High exact-loci NOT lifted (precise reasons — correct)
- **LendingTerm.onBid (H-03)**: stays INLINE_GUARD_REFUTED + UNKNOWN_OTHER (non-value class). Lens 2 (bad_debt_contagion)
  did not match in-span (no global-accumulator loss write resolved in the span); the contagion write is in a callee. A
  precise non-lens block — correct, not an FP. (Backlog: deeper bad-debt trace.)
- **ERC20RebaseDistributor.transfer (H-02)**: Lens 4 REFUTED (the transfer materializes BOTH sender+recipient rebase
  state). Correct refutation; the awarded theft is a subtler rebase-accounting flaw the lens conservatively declines.

## Held lens-match (NOT lifted; NOT an FP)
- **hybra GaugeCL.withdraw (share_transfer_theft → NEEDS_STATE_MACHINE_EVIDENCE)**: matched on transfer+shares+reward
  terms but the candidate is a STATE class, so the value-class lift path doesn't apply → held, never READY. Marginal
  match (withdraw is not a pure share-transfer); held status means 0 FP. Backlog: tighten Lens 4 to require an actual
  transfer-hook/from-to balance move, not a withdraw.

## Regressions (stable, no lens interference)
kelp getRsETHAmountToMint READY (D4.6) · blackhole claim_many READY (sibling) · L2Governor.execute READY (state-machine).
None matched any new lens.

## Tally
newly READY = 1 (correct, awarded H-04) · false READY = 0 · naming-only overreach = 0 · ECG hard-coding = 0 · severe
FP = 0. Consistent with verdict A.
