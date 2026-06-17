# notional — Phase 2: Selected loci + no-hindsight locks (PRE-REVEAL)

3 subtle loci (all BASE_BORN_INCOMPLETE; ≥3 mechanisms each; p242 families excluded).

## N-L1 — `AbstractYieldStrategy` conversion + effectiveSupply/escrow
- why selected: core share↔yieldToken valuation feeding `price()` (Morpho oracle) → mispricing = liquidation/borrow impact.
- base signal: accounting A1/A4 on convert*/_mintSharesGivenAssets/_burnShares.
- checkpoint signal: A1 rounding + A4 depletion cluster on conversions.
- what remained incomplete: how escrow/fee terms in the conversion can be pushed to misprice, and who profits.
- initial mechanisms: escrow-excluded-from-supply-but-not-balance; fee-subtracted-asymmetry; virtual-share ratio.

## N-L2 — `AbstractYieldStrategy` fee accrual (exp-decay + accrue-before-op + collectFees)
- why selected: fee feeds every conversion (`feesAccrued()` subtracted) → systematic value-routing.
- base signal: accounting A3/A2 on collectFees/_accrueFees.
- checkpoint signal: ST on collectFees/_accrueFees.
- what remained incomplete: whether accrual timing lets a depositor dodge or double the fee, or drift NAV.
- initial mechanisms: accrue-not-called-before-some-path; collectFees-deletes-without-reaccrue; exp-decay approx drift.

## N-L3 — `AbstractYieldStrategy` escrow + withdraw-request + transient valuation
- why selected: stateful escrow + pending-withdraw gating + transient `t_CurrentAccount` is a state-machine hazard.
- base signal: ST S1 reset/overwrite on reward/escrow paths.
- checkpoint signal: ST on initiateWithdraw/redeemNative; withdraw-request gates.
- what remained incomplete: whether escrow/withdraw-request state can be desynced to misvalue or block others.
- initial mechanisms: escrow double-count on re-initiate; withdraw-request-pending bypass via transfer; transient stale account.

**FREEZE:** final, recorded before reveal.
