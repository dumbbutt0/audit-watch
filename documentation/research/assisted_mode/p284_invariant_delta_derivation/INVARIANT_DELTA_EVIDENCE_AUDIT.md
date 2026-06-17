# P284 — INVARIANT_DELTA_EVIDENCE_AUDIT

Manual audit: the 1 SIBLING_REFERENCE_FOUND (the only deviation), 5 NO_REFERENCE candidates, the L2Governor.execute
regression. Question per item: reference basis real? observed real? expected source-backed? delta specific? attacker
valid? assertion implementable? any invented reference / naming-only overreach? status correct?

## A. The one deviation — claim_many (SIBLING_REFERENCE_FOUND, HIGH)
- **Reference basis real?** Yes. Sibling `claim` (same contract, stem `claim`) resolves `getOriginalOwner` inside an AVM
  block; `claim_many` shares the `transfer` mutating path and omits it. `sibling_function_parity_taxonomy.classify_pair`
  returns it as `recipient_parity`, weak=`claim_many`, HIGH (name-kin + ≥2 shared calls).
- **Observed/expected source-backed?** Yes — both are source expressions: observed = "`claim_many` omits
  `getOriginalOwner` on a shared mutating path"; expected = "apply `getOriginalOwner` as sibling `claim` does". Nothing
  invented.
- **Delta specific?** Yes — named missing component `getOriginalOwner`, recipient_parity.
- **Attacker / assertion?** attacker = permissionless `claim_many`; assertion = "result differs from the `claim`
  reference because `getOriginalOwner` is not applied" — implementable against the two siblings.
- **Status correct?** The EVIDENCE is correct and matches the documented awarded shape (M-04). The GATE status is
  `INLINE_GUARD_REFUTED` (D1 `ownerOf(` over-match) — a conservative, documented over-block, NOT a P284 error. No false
  READY produced.

## B. NO_REFERENCE sample (5 audited — correctly not lifted)
1. **Pair._mint** (SHARE_ROUNDING) — a conservation equation (`totalSupply`/balanceOf) is extractable (attached as a PoC
   assertion scaffold), but no sibling/registry/rounding deviation. `_mint`↔`_burn` are legitimate inverses, not a
   missing-component pair. **Correct** NO_REFERENCE.
2. **GaugeCL.claimFees** (ACCOUNTING) — value lives in `_claimFees`; no sibling omits a named component; no rounding
   evidence. **Correct.**
3. **GaugeV2.withdrawAllAndHarvest** (REWARDS) — siblings `withdraw`/`deposit` differ by design; no named missing
   component on a shared mutating path. **Correct** (no naming-only overreach — the LOW behavioral tier is excluded).
4. **HYBR._mint** (SHARE_ROUNDING) — mint helper; no deviation reference. **Correct.**
5. **StarklaneEscrow._depositIntoEscrow** (SHARE_ROUNDING, cross-chain) — external/dynamic dispatch; no in-source
   reference. **Correct** INSUFFICIENT/NO_REFERENCE.

## C. L2Governor.execute regression
Stays READY_FOR_POC_INTENT via the P281 D2 state-machine path; invariant-delta added a STATE_MACHINE consideration but
did not change the decision. PoC 2/2 PASS. **Correct.**

## D. Over-inference / invented-reference check
None. Every NO_REFERENCE record either carries only an equation SCAFFOLD (poc_assertion) with an explicit
"no deviation detector corroborates" assumption, or nothing. No corrected expression was invented; no naming-only
similarity produced a FOUND. The single FOUND is a real, documented awarded shape.

## E. Audit verdict
The deriver is **correct and high-value** (it recovered the M-04 sibling-recipient deviation from source alone, 0 FP),
and **strictly fail-closed** elsewhere (81/82 NO_REFERENCE). The lift blocker is upstream D1 granularity, not P284
precision. Consistent with verdict **B**.
