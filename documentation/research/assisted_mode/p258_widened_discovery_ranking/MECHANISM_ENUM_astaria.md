# astaria — Phase 3: Widened mechanism enumeration (PRE-REVEAL, FROZEN)

Per locus, mechanisms across the 7 families (A accounting · B convexity · C state-machine · D reentrancy ·
E migration · F identity · G temporal). Discovery only — no completion yet. Each: trigger · affected · ctrl ·
delta · victim/gainer · comparand · terminality · amp · assumptions · falsifier (compressed).

## A-L1 PublicVault epoch/withdrawReserve/slope
- **A1 (A) withdrawReserve rounding** — yIntercept/totalAssets rounding on processEpoch; ctrl L; delta L; tidy; falsifier: bounded.
- **A2 (C) epoch advanced with unsettled withdrawProxy** — processEpoch increments epoch even if prior withdrawProxy not fully funded / withdrawReserve not drained ⇒ LPs in epoch N stranded or paid from N+1; ctrl M; delta **H**; v/g LPs; comparand = epochData[epoch] invariant; terminality **H**; amp M; falsifier: a settle-guard blocks advance.
- **A3 (D) transferWithdrawReserve external transfer/drain before state finalize** — safeTransfer + `WithdrawProxy.drain` external calls around `withdrawReserve` updates ⇒ reentrancy/ordering; ctrl M; delta M; comparand = CEI; term M; falsifier: nonReentrant + checks-effects.
- **A4 (G) slope/_accrue not updated at epoch boundary** — interest slope/yIntercept stale across processEpoch ⇒ NAV/withdraw mis-valued; ctrl L (time); delta M; comparand = _accrue before epoch math; term M; falsifier: _accrue called first.

## A-L2 LienToken._buyoutLien
- **A1 (A) buyout amount excludes/duplicates accrued interest** — debt transferred without exact accrued interest; ctrl M; delta M; comparand = makePayment interest math; tidy-ish; falsifier: buyout uses same accrue.
- **A2 (G) stale accrual at buyout** — interest not accrued immediately before buyout ⇒ buyer over/under-pays; ctrl M; delta M; term M; comparand = _accrue; falsifier: accrue-on-buyout.
- **A3 (F) buyout payment to wrong principal** — payment routed to vault/old holder vs the lien's actual payee; ctrl M; delta M; v/g clear; comparand = lien.payee; falsifier: payee enforced.
- **A4 (D) buyout external-call reentrancy** — token transfers mid-buyout; ctrl L; falsifier: guard.

## A-L3 PublicVault redeem/redeemFutureEpoch
- **A1 (A) redeem share/asset rounding** — ERC4626 rounding; tidy; delta L; falsifier: virtual-offset.
- **A2 (C) future-epoch redemption double-counts withdrawReserve** — redeemFutureEpoch mints withdrawProxy shares + increments withdrawReserve; epoch advance could double-serve; ctrl M; delta **H**; comparand = withdrawReserve conservation; term **H**; falsifier: per-epoch reserve isolation.
- **A3 (B) convexity redeeming across epochs** — splitting redemption across epochs yields more than one-shot; ctrl M; delta M; falsifier: linear share math.

**FREEZE.** (no completion in this phase)
