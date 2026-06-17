# P203 — recommendation

## Final decision: `V2_GATE_FAILED_FALSE_HIGH`
The v2 "independent source-substantiation" precondition did **not** fix P202's over-confirmation. Scored over frozen
P202 artifacts, v2 regrade authored by a **fresh key-blind firewall subagent** (`e2100588`; provenance recorded —
valid, not orchestrator-applied).

### Results
- ✅ **H-01 retained HIGH_CONFIRMED**; **0 genuine Highs demoted to Medium** (H-02/03/04 stayed NEEDS_HARNESS). So v2
  does no harm to High preservation.
- ❌ **M-03 (receiveFromBridge) still HIGH_CONFIRMED** on all 3 surfaces; **over-HIGH on matched awarded-Mediums
  unchanged** ([01,02,03]); **false-High surfaces unchanged** ([01,02,03,06]). Only 1 of 8 v1-HIGH mechanisms
  (decent-06 M1) downgraded, and its surface stayed High via M2.
- Per the decision rule, `V2_GATE_FAILED_FALSE_HIGH` ("M-03 remains High without source-proven custody/value-flow,
  or false-Highs remain mostly unchanged"). Not FAILED_FALSE_DEMOTION (H-01 kept). Not INVALID_RUN (key-blind fresh
  subagent applied a general, pre-written rule).

### The decisive insight (why this phase matters)
P202 hypothesised the over-confirmation was "the gate trusting the blind layer's asserted magnitude." P203 **refutes
that as the sole cause**: an **independent, key-blind, source-reading agent reaches the same HIGH** on
receiveFromBridge — it treats the arbitrary `executor.execute` capability (and the existence of balance variables) as
source-proven material value-flow. The real gap is **worst-case capability vs realized impact**: source proves
"arbitrary-call capability," which a reviewer rates High, while the C4 judges rated **realized** impact (fee/signature
bypass; UTB custodies no funds between txs) **Medium**. A **static** source-substantiation precondition is
**interpretable/gameable** and cannot separate the two (see `HIGH_PRECONDITION_AUDIT.md`).

### Recommended next (each needs explicit go — NOT actioned here)
1. **Do not pursue a static precondition rule (v3-static) for this gap.** P203 shows it doesn't bite — an independent
   reviewer confirms capability-as-High.
2. **Move to a realized-impact / PoC-harness magnitude standard** for HIGH: require a concrete attacker-tx that moves
   **material value under the deployed configuration** (the project's existing **L3 PoC standard**), not static
   source-substantiation. Re-test on decent: H-01 (setRouter→mint) should produce a passing L3 PoC; M-03
   receiveFromBridge should fail to produce material value movement (UTB holds no funds) → demote. This is the
   precise next lever.
3. **Keep v2's one win**: the swapExactIn/Out → fee-bypass downgrade (decent-06 M1) is correct; the bounded/
   self-funded check works on clear cases.
4. Deep-pass recall (H-02/03/04 recall-misses) and the oracle track remain separate.

### Cross-arc synthesis
P200 demotion-partial · P201 demotion-clean/confirmation-untestable · P202 confirmation-works/demotion-regresses ·
**P203 the regression is NOT a blind-trust artifact — it is a capability-vs-realized-impact gap that static rules
cannot close.** The severity-calibration frontier now points to **harness/PoC-grade magnitude**, not more static
gating.

## Acceptance criteria — met
Frozen P202 artifacts reused (no rerun) ✓ · no production files modified ✓ · v2 rule written before application ✓ ·
every HIGH_CONFIRMED required independent source-backed evidence (audited; over-reaches flagged) ✓ · H-01 and M-03
explicitly tested ✓ · v1 vs v2 scored separately ✓ · production hashes byte-identical START==END ✓ · JSON valid ✓ ·
no key-backfit into rules (general rule; key-blind regrade) ✓.
