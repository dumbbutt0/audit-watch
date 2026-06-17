# notional — Phase 3: Mechanism enumeration (PRE-REVEAL, FROZEN)

≥3 mechanisms/locus; each: trigger · affected accounting/state · controllability · value-delta · victim/gainer ·
comparand · terminality · amplification · assumptions · falsifier.

## N-L1 conversion + effectiveSupply/escrow
- **M1 (tidy) virtual-share/virtual-yield ratio rounding** — trigger: tiny deposits; state: shares↔yieldToken;
  ctrl M; delta L (dust); v/g weak; comparand = ERC4626 virtual-offset pattern; terminality L; amp M (repeat);
  assumptions: rounding accumulates; falsifier: VIRTUAL offsets neutralize it.
- **M2 (messy) escrow-excluded-from-supply-but-not-from-balance** — trigger: an account `initiateWithdraw`s
  (shares leave `effectiveSupply` but their yield tokens stay in `_yieldTokenBalance()`); state: effectiveSupply vs
  balance; ctrl M; delta **H** (conversion rate for remaining holders inflated by escrowed holders' yield tokens);
  v/g **clear** (loser = escrowed withdrawer / protocol; gainer = active converters during the escrow window);
  comparand = effectiveSupply intentionally subtracts escrow → the balance should too; terminality **H** (value
  redistributed, realized on convert); amp H (size the withdraw); assumptions: convert happens during escrow
  window; falsifier: withdraw request removes the yield tokens from balance synchronously.
- **M3 (messy) uncollected-fee NAV drift in price()** — trigger: time passes without collectFees; state:
  `feesAccrued()` compounds in every conversion → `price()` drifts down then jumps at collect; ctrl L (time);
  delta M; v/g M (borrowers liquidated on a drifting oracle price); comparand = a NAV should be continuous; term M;
  amp M; assumptions: Morpho uses price() live; falsifier: fee is negligible / price() consumers tolerant.

## N-L2 fee accrual
- **M1 (tidy) exp-decay Taylor-approximation error** — 3-term `e^x` approx; ctrl L; delta L; comparand = exact exp;
  term L; amp L; falsifier: bounded error within precision.
- **M2 (messy) accrue-timing fee dodge / NAV inconsistency** — trigger: a path that converts/mints using
  `feesAccrued()` without first `_accrueFees()` committing state (accrue returns early within a block; ordering
  across entry points); state: s_accruedFeesInYieldToken vs live additional; ctrl **M**; delta M; v/g M (new
  depositor mints at stale-fee price ⇒ dilutes existing or dodges fee); comparand = "_accrueFees must precede any
  mint/burn" (the code comment); terminality M; amp M; falsifier: every entry path provably accrues first.
- **M3 (messy) collectFees post-transfer accrual-base shift** — trigger: collectFees transfers then deletes
  accrued; next `_calculateAdditionalFeesInYieldToken` base (`balance - accrued`) shifts; ctrl L; delta M; v/g M;
  comparand = fee base should be invariant to collection; term M; amp M; falsifier: re-accrual before next op corrects it.

## N-L3 escrow + withdraw-request + transient
- **M1 (tidy) transient t_CurrentAccount stale across calls** — clean transient-state bug; ctrl M; delta M;
  comparand = clearCurrentAccount exists; term M; amp L; falsifier: router always clears.
- **M2 (messy) escrow double-count / effectiveSupply desync** — trigger: `initiateWithdraw` adds to
  `s_escrowedShares` (no idempotency vs an existing request); state: escrowedShares vs actual escrowed; ctrl **M**;
  delta **H** (effectiveSupply understated ⇒ remaining holders' conversion inflated, or underflow); v/g clear;
  comparand = escrow should equal outstanding withdraw shares; terminality **H** (persistent supply desync); amp H;
  falsifier: a single-request-per-account invariant enforced elsewhere.
- **M3 (messy) withdraw-request-pending bypass via tokenized/transferred request** — trigger: holding a position +
  a pending (transferred) withdraw request; ctrl M; delta M; v/g M; comparand = the pending-request gates; term M;
  amp M; falsifier: transfer of requests fully blocked.

**FREEZE:** final before ranking ablation + reveal.
