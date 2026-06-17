# P200 — failure cases (described, not patched)

## A. Over-HIGH the gate FAILED to fix (oracle/precision) — the decisive failure
These are mechanism-matched **awarded-Medium** findings the gate kept at HIGH_CONFIRMED.

### predy-09 → M-04 (Chainlink `latestRoundData` staleness) — awarded **Medium**, gate **HIGH_CONFIRMED**
- Blind selected[0]: "Chainlink latestRoundData accepted with no staleness/round-completeness, only require(>0)".
  Exactly M-04.
- Gate rationale (frozen): graded HIGH because "missing staleness guard → insolvency/wrongful-liq, permissionless"
  — applying P199's revert-lend H-05 *oracle-manipulation→insolvency=High* precedent.
- **Why it's a failure:** predy's judges scored Chainlink staleness **Medium** (bounded mispricing / liveness in
  this protocol's context, not a proven drain). The discriminator's oracle rule **over-rates** here. **Gate defect**
  (the rule, not insufficient evidence): the High dimensions were asserted, not proven, yet not routed to harness.

### predy-10 → M-03 (negative-tick rounding) — awarded **Medium**, gate **HIGH_CONFIRMED**
- Blind selected[1] = M-03 exactly (integer-division truncation on negative ticks). But the surface's HIGH grade
  came from selected[0] = "TWAP degrades to spot at low cardinality → insolvency", a manipulation claim that is
  **not separately awarded**.
- **Why it's a failure:** the awarded reality on this surface is a Medium precision bug; the gate rated the surface
  High on a *different, unawarded* manipulation mechanism. Over-HIGH via mechanism substitution.

### predy-07 → M-04/M-08 (loose) — awarded **Medium**, gate **HIGH_CONFIRMED**
- isLiquidatable oracle-usage overlaps the PriceFeed Medium findings. Same oracle over-rating as predy-09 (looser
  locus match). Reinforces the oracle-severity generalization gap.

## B. Genuine-High folded under a Medium surface grade (multi-mechanism)
### predy-06 → H-02 (negative-margin bypass, loss to protocol) — awarded **High**
- predy-06 found **both** M-06 (recipient bricks liquidation, Medium) as selected[0] **and** H-02 (liquidator dodges
  negative-margin compensation, High) as selected[1]. The surface-level gate label = **Medium** (driven by the
  primary M-06 DoS).
- **Why it matters:** a *per-mechanism* gate (as P199 actually proposes) would grade H-02 High and M-06 Medium
  separately. The P200 application graded **one label per surface**, so H-02 is under-represented. This is a
  **methodology gap (surface-level vs mechanism-level)**, not a calibration error in the rule — but on a corpus
  with more multi-mechanism Highs it would cause genuine-High demotions. Flagged for any production design.
- Note: this is the *only* awarded-High the blind run found by mechanism. H-01/H-03/H-04 were recall misses (§D).

## C. Unawarded HIGH_CONFIRMED (recall false-positives, not severity-gate failures)
- predy-08 (unchecked `IHooks(msg.sender)` + checkSafe-after-callback), predy-12 (settlement buy() accounting
  shortfall), predy-16 (Perp.reallocate pool-can-go-negative). None map to an awarded H/M. The severity gate cannot
  fix a recall FP — these inflate the HIGH_CONFIRMED bucket but are a *recall/precision* issue. (predy-08's
  callback-to-caller may be by design; predy-12/16 may be QA/Low or simply not real.)

## D. Recall misses on awarded Highs (wrong mechanism — not severity events)
- **H-01** (reallocation uses manipulable `slot0` price) and **H-03** (one pair steals another's Uniswap liquidity
  during reallocate with shared pool/ticks): the reallocate surfaces (predy-02, predy-16) found *different*
  mechanisms (permissionless-timing griefing; stale-index/pool-negative), not the awarded slot0/shared-tick ones.
- **H-04** (liquidation transfers from Market instead of liquidator when remainingMargin<0): predy-06 touched the
  negative-margin branch but framed H-02, not H-04's wrong-source-transfer.
- These are **deep-pass recall/mechanism-selection** gaps (the P183–P188 frontier), independent of the severity
  gate under test.

## Summary
The gate's **one clean win** is the griefing/DoS demotion (predy-06 M-06 → Medium). Its **decisive failures** are
oracle/precision over-HIGH (A) that did not generalize from P199's in-sample fit, plus a surface-vs-mechanism
folding risk (B). No clean false-demotion of a separately-found awarded High to Medium/None occurred.
