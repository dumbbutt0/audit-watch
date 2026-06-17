# ethos — Phase 3: Widened mechanism enumeration (PRE-REVEAL, FROZEN)

Per locus, mechanisms across the 7 families. Discovery only — no completion. (compressed fields)

## E-L1 ActivePool._rebalance
- **E1 (A) profit double-count / recalc mismatch** — `profit` first = convertToAssets−yieldingAmount, then recalc
  = bal+yieldingAmount−collAmount; the two can disagree ⇒ over-distribute profit; ctrl L; delta M; comparand = collAmount invariant; tidy-ish; falsifier: recalc exact.
- **E2 (B) ERC4626 convertToAssets convexity / share-price manipulation** — yieldGenerator share price (donation/
  first-deposit) skews `sharesToAssets` ⇒ phantom profit or under-withdrawal; ctrl M; delta **H**; v/g SP/stakers vs attacker; comparand = real assets; terminality H; amp H; falsifier: vault inflation-safe.
- **E3 (E) ERC4626 withdraw rounding leaves yieldingAmount desync** — `withdraw(netAssetMovement)` burns shares
  rounding-up ⇒ yieldingAmount bookkeeping drifts from actual; ctrl M; delta M; comparand = yieldingAmount==assets; term M; falsifier: reconcile post-withdraw.
- **E4 (G) drift threshold / stale yieldingAmount over time** — yieldingPercentageDrift gate skips rebalance ⇒ stale allocation; ctrl L; delta M; falsifier: bounded.
- **E5 (A) profit distributed before withdrawal settles** — split transfers treasury/staking/SP from balance that
  may not yet hold withdrawn assets ⇒ shortfall; ctrl L; delta M; term M; falsifier: ordering safe.

## E-L2 StabilityPool.offset
- **E1 (A) P/S product reward rounding** — compounded-deposit product math rounding; tidy; delta L; falsifier: bounded.
- **E2 (G) scale/epoch snapshot drift** — error in scale change / epoch reset ⇒ depositor reward over/under-credited
  (classic Liquity scale bug class); ctrl L; delta M; v/g depositors; comparand = Liquity reference; term M; falsifier: scale handling correct.
- **E3 (B) last-depositor / tiny-pool convexity** — offset when pool ≈ debt ⇒ rounding amplified; ctrl M; delta M; falsifier: min-deposit.

## E-L3 RedemptionHelper.redeemCollateral / SortedTroves.reInsert
- **E1 (A) redemption fee / base-rate accounting** — fee/base-rate update math; tidy; delta L; falsifier: bounded.
- **E2 (C) partial-redemption reInsert leaves trove mis-sorted / stuck** — partial redemption reinserts with stale
  NICR/hint ⇒ sorted-list invariant broken, redemption skips/strands; ctrl M; delta **H**; comparand = SortedTroves order invariant; terminality H; amp M; falsifier: reInsert recomputes NICR.
- **E3 (F) redeemer redeems against another's trove with cross-collateral mismatch** — multi-collateral: redeemer
  vs trove owner vs collateral type; ctrl M; delta M; comparand = collateral binding; falsifier: per-collateral enforced.
- **E4 (G) base-rate decay timing / redemption ordering across block** — ctrl L; delta M; falsifier: decay correct.

**FREEZE.** (no completion in this phase)
