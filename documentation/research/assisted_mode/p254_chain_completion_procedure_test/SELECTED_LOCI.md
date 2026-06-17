# P254 — Phase 2: Selected loci + no-hindsight locks (PRE-REVEAL)

Four loci selected from the frozen Phase-1 set, **before the answer key is opened**. Coverage requirement met:
≥1 state-transition locus (B-1, B-4) and ≥1 accounting/cross-contract-like locus (B-2 accounting, B-5
cross-contract). All four are tagged `BASE_BORN_INCOMPLETE` — i.e. base births a candidate but did **not**
complete the chain, which is exactly where the routine can add value. Trivial candidates excluded; the two
`CHECKPOINT_HIT_SUSPICIOUS_LOCUS`-only items (PoolV3/Flashlender/quotas) excluded (no born candidate to
complete). B-3 (near-complete oracle) excluded as least-informative for a completion test.

Each locus carries a **no-hindsight lock** (written now, before reveal) to prevent post-reveal credit leakage:
*why selected · which signal selected it · what base already completed · what remained incomplete before the
five-operation routine.*

---
## L1 ← B-2 — `AuraVault.claim` (accounting / AAS)
- **Why selected (pre-reveal):** strongest blind candidate; caller fully controls the reward `amounts[]` that
  are paid out, and the payout is not reconciled against actually-earned rewards — a classic value-extraction shape.
- **Signal that selected it:** base rank #1 + accounting checkpoint A1/A4 records on `claim`/`_previewReward`.
- **What base already completed:** observed "amounts unvalidated; paid to msg.sender."
- **What remained incomplete (gap for routine):** no concrete attacker profit computed — is there a *positive*
  delta to the attacker (do they receive more value than the WETH they pay in), is it permissionless, and what
  is the protocol's loss? Chain from observation → quantified theft not built.

## L2 ← B-4 — `CDPVault.liquidatePosition` (state-transition / IDC / AAS)
- **Why selected (pre-reveal):** liquidator-chosen `repayAmount` drives three different quantities
  (`takeCollateral`, `deltaDebt`, `penalty`) with a visible asymmetry between debt reduced and cash/collateral moved.
- **Signal that selected it:** base rank #2 + accounting A3 double-count / A4 depletion on liquidation.
- **What base already completed:** noticed `deltaDebt = repayAmount·penalty` vs cash flows using `repayAmount`/`penalty`.
- **What remained incomplete (gap for routine):** invariant-delta not computed — after a (possibly repeated /
  dust) liquidation, does total debt reduction match value extracted from the position/pool, who is the net
  loser, and can a liquidator profit beyond the intended penalty? Terminal state of an unsafe position not traced.

## L3 ← B-5 — `SwapAction.swap` + `PositionAction` residual recipient (cross-call identity)
- **Why selected (pre-reveal):** EXACT_OUT leftover and `pendleJoin` full-balance usage route funds to a
  caller-controlled `recipient` across the delegatecall proxy/router/module layers — prime CCIT surface.
- **Signal that selected it:** base rank #3 + accounting A4 depletion / A5 index on `swap`/`transferAndSwap`.
- **What base already completed:** saw `safeTransfer(recipient, limit − retAmount)` (EXACT_OUT) and
  `balanceOf(address(this))` in `pendleJoin`.
- **What remained incomplete (gap for routine):** identity not tracked across hops — does the `recipient`/
  beneficiary that *receives* residual match the principal whose funds were *spent*; can an attacker set
  `recipient = self` while the spent funds belong to the proxy/another user; is the affected principal ≠ checked principal?

## L4 ← B-1 — `StakingLPEth.cooldownAssets/cooldownShares` (state-transition)
- **Why selected (pre-reveal):** clean S1 reset/overwrite shape — `cooldownEnd` overwritten (not max'd) on every call.
- **Signal that selected it:** state-transition checkpoint S1 reset/overwrite + accounting A3 on cooldown*.
- **What base already completed:** saw `cooldownEnd = block.timestamp + cooldownDuration` overwrite while `underlyingAmount += assets`.
- **What remained incomplete (gap for routine):** repetition/edge state not simulated — does a second call by a
  user mid-cooldown strand already-cooled funds; is it self-inflicted only or attacker-forceable on another
  user; what is the terminal state (funds recoverable or locked)?

---
**FREEZE:** these four selections + locks are final, recorded before reveal.
