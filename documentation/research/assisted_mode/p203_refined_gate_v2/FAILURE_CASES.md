# P203 — failure cases (v2 gate)

## A. M-03 (receiveFromBridge) still HIGH_CONFIRMED — the decisive v2 failure
- Surfaces decent-01/02/03; awarded **Medium** (M-03). v1 HIGH → **v2 HIGH (unchanged).**
- The fresh key-blind v2 agent retained HIGH, citing arbitrary `executor.execute(target,payload,paymentOperator)`
  with UTB as caller as source-proven material (custody marked `ACCOUNTING_BALANCE_PROVEN`).
- **Why v2 didn't fix it:** the over-confirmation is NOT (only) "the gate trusting the blind layer's asserted
  magnitude" — an **independent source review reaches the same High**. The disagreement with the C4 Medium rating is
  a **worst-case-capability vs realized-impact** severity gap. The v2 precondition ("source-proven custody/value-flow
  at the vulnerable point") is satisfiable by *arbitrary-call capability*, so it does not separate the two.

## B. Unawarded false-Highs persist
- decent-06 (UniSwapper): v2 downgraded M1 (swapExactIn/Out — attacker funds own swap → fee/routing bypass) but
  **retained M2** (swapNoPath drain) HIGH → surface stays High. Net: false-High persists.
- decent-12 (DecentEthRouter redeem double-withdrawal): retained HIGH despite the blind output's own note that the
  attacker "needs a mechanism to receive dcntEth" (precondition not fully proven). Unawarded false-High persists.
- decent-03 M2 (UTB impersonation): retained HIGH on an "assumes UTB holds approvals/roles elsewhere" (unseen) basis.

## C. The one v2 success (and the one true High)
- **decent-06 M1 downgraded** (HIGH → MEDIUM): correct — attacker funds their own swap; proven impact is bounded
  fee/routing bypass, custody NOT_PROVEN. This is the v2 rule working as intended on a clear case.
- **decent-09 / H-01 retained HIGH**: correct and unimpeachable — setRouter→mint/burn controls the token supply
  inside the contract under trace. No false demotion.

## D. What did NOT fail
- **0 genuine Highs demoted to Medium/None.** H-01 retained; H-02/H-03/H-04 (partial matches) stayed NEEDS_HARNESS.
  So v2 is not a FALSE_DEMOTION failure — it is a FALSE_HIGH failure.

## Root cause & fix direction
The v2 `custody_value_flow_proof` precondition is **interpretable/gameable**: an independent reviewer treats
arbitrary-execution capability or the mere existence of a balance variable as "value-flow proven." Static
source-substantiation cannot separate worst-case capability from realized, deployment-conditioned impact. **The fix
is a realized-impact / PoC-harness magnitude standard** (the project's L3 PoC standard: a concrete attacker tx that
moves material value under the deployed config), not a static precondition rule. The severity-calibration frontier
therefore moves from "static gate rule" to "harness-grade magnitude proof."
