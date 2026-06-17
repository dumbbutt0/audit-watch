# astaria — Phase 2: Selected loci + no-hindsight locks (PRE-REVEAL)

3 subtle loci (BASE_BORN_INCOMPLETE; ≥2 mechanisms; multi-family).

## A-L1 `PublicVault` epoch / withdrawReserve / slope
- why selected: epoch state-machine + withdraw-reserve transfer + slope/interest accrual is Astaria's core, high-impact.
- base signal: accounting A2/A5 on processEpoch; ST S3 on transferWithdrawReserve/processEpoch.
- checkpoint signal: ST dual-state on epoch transitions.
- what base knew: epoch increments, yIntercept decrement, withdrawReserve transfer+drain.
- what remained incomplete: which epoch-boundary accounting/state desync or reentrancy is exploitable.
- expected subtle class: state-machine (C) / temporal (G) / reentrancy (D).
- why not trivial: ≥4 plausible mechanisms across families.

## A-L2 `LienToken._buyoutLien`
- why selected: cross-lienholder debt/interest transfer with accrual + identity.
- base signal: accounting A on _buyoutLien.
- checkpoint signal: accounting A2 on buyout/payDebt.
- what base knew: buyout moves debt + pays interest.
- what remained incomplete: stale accrual at buyout / wrong recipient.
- expected subtle class: temporal (G) / identity (F) / accounting (A).
- why not trivial: ≥3 mechanisms.

## A-L3 `PublicVault.redeem` / `redeemFutureEpoch`
- why selected: LP redemption across epochs via withdrawProxy.
- base signal: accounting A1 on redeem; ST on redeemFutureEpoch.
- checkpoint signal: ST dual-state on future-epoch redemption.
- what base knew: redemption queued to future epoch.
- what remained incomplete: across-epoch share/asset accounting drift.
- expected subtle class: state-machine (C) / accounting (A) / convexity (B).
- why not trivial: ≥3 mechanisms.

**FREEZE:** final before enumeration/reveal.
