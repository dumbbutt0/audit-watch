# P202 — failure cases (described, not patched)

## A. False HIGH_CONFIRMED on awarded-Medium M-03 (the decisive failure)
**Surfaces decent-01/02/03 · mechanism: missing access control on `UTB.receiveFromBridge`.**
- Awarded severity: **Medium** (M-03 — "allows UTB swaps without bridge fees while bypassing fee/swap-instruction
  signature verification").
- Blind ceiling: CRITICAL. Refined gate: **HIGH_CONFIRMED** (×3 surfaces).
- Why wrong: the realistic impact is fee/signature bypass, not theft, because UTB does not custody user funds
  between transactions — the judges rated it Medium. The blind layer **over-claimed** permissionless theft of
  "UTB-held funds." The gate's `loss_magnitude=material` / `exploit_executability=executable` dimensions were
  satisfied by the blind agent's confident assertion, so reject-first did not trigger.
- Classification: **gate over-confirmation driven by inherited blind over-claim** — the gate trusts the frozen
  output's magnitude claim and has no independent precondition check (does UTB actually hold funds?).

## B. False HIGH_CONFIRMED on unawarded mechanisms
- **decent-06** (UniSwapper `swapExactIn`/`swapNoPath` public, drain): not in the awarded H/M set (M-01 is a
  different swap-data-outdated mechanism). Gate HIGH_CONFIRMED → false High on an unawarded mechanism (recall FP the
  severity gate cannot fix, but it confirmed it High, inflating the High bucket).
- **decent-12** (DecentEthRouter `redeemEth`/`removeLiquidity` double-withdrawal): the HIGH_CONFIRMED mechanism is
  the double-withdrawal, which is **not** in the awarded set. (`metrics.json` loosely links decent-12 to H-04 via a
  partial reserve match, but the *confirmed-High mechanism* is the unawarded double-withdrawal — so honestly this is
  a false/unawarded High, not an H-04 preservation.)

## C. Recall misses on awarded Highs (deep-pass recall, not severity-gate failures)
- **H-02** (missing min-gas for LayerZero → destination execution fails): decent-10 found gas/LZ-fee mechanisms but
  not the exact min-gas-check-missing one → partial. Gate NEEDS_HARNESS (correctly not demoted).
- **H-03** (DecentBridgeExecutor.execute fail → funds to random address): decent-13 traced the right surface but
  found stuck-funds/approval, not the "funds to random address" mechanism → recall miss. Gate NEEDS_HARNESS.
- **H-04** (insufficient destination WETH reserves → user loses tx): decent-11 found the reserve-fallback accounting
  drift, framed differently → partial. Gate NEEDS_HARNESS.
- These are P183–P188 **deep-pass recall** gaps (wrong/partial mechanism on the right surface), independent of the
  severity gate. They are the reason only 1/4 awarded Highs was confirmable.

## D. What worked (no false demotions)
- **H-01** (DcntEth `setRouter` public → mint/burn): exact mechanism match, gate HIGH_CONFIRMED. ✅
- **0 genuine Highs demoted to Medium/None.** Every partial-match awarded-High went to NEEDS_HARNESS, not Medium.
- **M-04** (UTBFeeCollector fixed-fee) → Medium; **decent-14** access-control DoS → Medium. DoS/precision/admin
  demotion still works where the blind layer did not over-claim theft.

## Summary
The gate's reject-first logic correctly **demotes** DoS/precision/admin and **does not demote** genuine Highs, and
it **positively confirmed** a real permissionless-theft High (H-01). Its failure is **over-confirmation**: it
inherits the blind layer's magnitude over-claim (M-03 receiveFromBridge) and confirms unawarded mechanisms High
(decent-06/12). The fix is an **independent magnitude/precondition gate** that does not trust the blind output's
asserted impact — plus deep-pass recall improvements so more awarded Highs are matchable (H-02/03/04).
