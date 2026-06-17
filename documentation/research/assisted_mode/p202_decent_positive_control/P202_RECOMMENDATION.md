# P202 — recommendation

## Final decision: `REFINED_GATE_PARTIAL`
**High-confirmation path validated; Medium-demotion regresses via inherited over-claim.** The calibration was
authored by a **fresh firewall subagent** (orchestrator was PCS-contaminated and did NOT apply the gate), so this is
a **valid out-of-sample result — NOT CONTAMINATED_UPPER_BOUND.**

### What was proven (positive — the campaign's first)
- **The gate CONFIRMS a genuine contract-level High out-of-sample.** H-01 (DcntEth `setRouter` public → arbitrary
  mint/burn, permissionless theft) was matched exactly and graded **HIGH_CONFIRMED**. P201 produced 0 HIGH_CONFIRMED
  with 0 matched contract-Highs; P202 closes that gap — the High-confirmation path works.
- **Zero genuine Highs demoted to Medium/None.** The other awarded Highs (H-02/H-03/H-04), only partially matched by
  the blind layer, were routed to **NEEDS_HARNESS**, not demoted — the correct reject-first middle.
- **DoS/precision/admin demotion still works** (M-04 → Medium, decent-14 → Medium).

### What failed (negative — the new lever)
- **HIGH-bucket precision is poor (~1/6).** The gate over-confirmed the awarded-**Medium** M-03 (missing AC on
  `receiveFromBridge`) as **HIGH on 3 surfaces**, plus 1–2 unawarded mechanisms (decent-06 public-swap; decent-12
  double-withdrawal). On the matched awarded-Medium subset, ceiling over-HIGH 5/5 → calibrated 3/5 (only 2 fixed) —
  a **regression** vs P201's clean demotion.
- **Root cause:** the gate **trusts the blind layer's asserted magnitude/exploitability**. When blind *recall*
  over-claims theft (here, ignoring that UTB holds no funds between txs — the precondition that made judges rate
  receiveFromBridge Medium), the reject-first dimensions (`loss_magnitude=material`, `executable`) are satisfied by
  the assertion and the gate confirms High.

### Why PARTIAL (decision-space justification)
- Not `REFINED_GATE_VALIDATED_TWO_SIDED`: false HIGH_CONFIRMED is not "acceptably low" and Medium over-HIGH did not
  drop materially (regressed on M-03).
- Not `REFINED_GATE_FAILED_FALSE_DEMOTIONS`: **0** source-proven contract-Highs were demoted to Medium/lower.
- Not `CONTAMINATED_UPPER_BOUND`: the fresh firewall subagent (not the contaminated orchestrator) authored the
  calibration; provenance recorded.
- `REFINED_GATE_PARTIAL` per its definition: *High preservation works but Medium demotion regresses.*

## Cross-run synthesis (the unifying finding)
| run | demotion axis | confirmation axis |
|---|---|---|
| P200 predy | partial | 1 High under-graded |
| P201 zetachain | **clean** (6/7→0/7) | untestable (Highs off-chain) |
| P202 decent | **regresses** (over-confirms over-claimed Medium) | ✅ **works** (H-01 confirmed; 0 false demotions) |

The two axes have **never been clean simultaneously**. The lever is now precise: **the severity gate must not
inherit the blind layer's magnitude/precondition assertion.** A High requires an *independent* check that the
value-extraction precondition actually holds (e.g., funds are actually custodied / reachable), not just that the
blind output asserted it.

## Recommended next (each needs explicit go — NOT actioned here)
1. **Do not wire the gate yet.** It now has a confirmation path (good) but poor High precision (over-confirms
   over-claimed mechanisms). Wiring it would inflate Highs.
2. **Add an independent magnitude/precondition sub-check** to the gate's class-A/E HIGH path: require the
   value-extraction precondition to be source-substantiated (not merely asserted by the blind output) before
   HIGH_CONFIRMED; otherwise → NEEDS_HARNESS. Re-validate on decent (should demote M-03 receiveFromBridge to
   Harness/Medium while keeping H-01 High).
3. **Deep-pass recall** (P183–P188): H-02/H-03/H-04 were partial/recall-miss matches → improving mechanism-level
   recall would let more awarded Highs be confirmable (and is independent of the severity gate).
4. Oracle track (separate): oracle-rich corpus search → oracle gate validation.

## Acceptance criteria — met
decent positive-control ✓ · PCS contamination caveat documented ✓ · **fresh firewall subagent applied the gate** ✓
· blind frozen before calibration (`54abf9ca`) ✓ · calibration frozen before full key (`90cf2a4f`) ✓ ·
mechanism-level scoring ✓ · High-preservation measured ✓ · Medium-demotion measured ✓ · secondary-High preservation
measured (per-mechanism, 33 mechs) ✓ · no production files modified ✓ · production hashes byte-identical START==END ✓
· JSON valid ✓ · `fabrication_rate=0` ✓.
