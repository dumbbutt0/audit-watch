# P120 — Decision: FeeCollector.collectProtocolFees (NOVEL candidate)

## Terminal state: **KILLED_RUNTIME**

Runtime decided. The harness refuted the theft/redirection hypothesis with executed assertions — not source-only
reasoning.

| KILLED condition (spec) | Evidence (runtime) |
|---|---|
| the suspected exploit cannot occur | Cases A/B/C: the permissionless caller (`attacker`, an arbitrary EOA) ends every call with **token balance == 0**; no value flows to the caller (PASS). |
| recipients are not caller-controlled | Case A: fees split `treasury` (20%) + voter-resolved `feeDist` (80%); Case B: `collectProtocol` recipient == `treasury`; **Case C: even an attacker-DEPLOYED pool routes to the hardcoded `treasury`, not the attacker** — the arbitrary `pool` argument cannot steer funds to the caller (PASS). |
| the accounting quirk is not profitable | Case D: the `balanceOf(this)` notify amount sweeps a pre-existing residual into the collected pool's `feeDist` (cross-pool misattribution), but it requires a **donation (self-loss)** to the FeeCollector — the attacker gains nothing (PASS). |

**Verdict:** the high-ranked, permissionless-flagged `collectProtocolFees` is a permissionless *trigger* with fully
hardcoded / voter-resolved recipients (`treasury`, `address(this)`, `feeDist`). A permissionless caller cannot
extract or redirect protocol fees, and the arbitrary-`pool` argument cannot redirect funds to the caller →
**KILLED_RUNTIME**. A clean runtime REFUTATION of a NOVEL candidate (the methodology that CONFIRMED P117's true
positive and KILLED P118's false lead also correctly KILLS this one).

## Observation recorded (not a finding here)
The `amount = token.balanceOf(address(this))` notify amount (rather than the collection delta) means any residual
the FeeCollector holds is attributed to whichever pool is collected next — a cross-pool *misattribution*. It is not
attacker-profitable (needs a donation), so it is out of scope for the theft/redirection question and is recorded as
an observation, not promoted to a finding. No severity assigned.

## Scope / honesty notes
- Hypothesis tested = theft / redirection by a permissionless caller (the high-value reading of a permissionless
  fee-collection function). The trusted `voter`'s gauge/feeDist resolution is taken as honest (governance model).
- **No severity assigned**, no report, no submission package, no READY state, no production wiring (hard stops).
- Novel candidate — but the verdict is KILLED, so there is nothing to submit regardless.

## Hard-stop self-check
- KILLED_RUNTIME claimed only with passing runtime tests (Cases A/B/C/D all PASS, executed). ✓
- No source-only reasoning used as runtime proof — the balances/recipients are executed assertions. ✓
- No severity / report / submission / READY token; no production wiring. ✓
- ramses `contracts/` (src) **unmutated** — `FeeCollector.sol` imported via remapping; the harness lives only in the
  standalone `/tmp/p120-feecollector-harness/` project. ✓
