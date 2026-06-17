# P212 Stage 2 — misses & false positives

## False positives: 0
Nothing was promoted as a confirmed submittable finding except SOPH-03, which is a genuine awarded High. SOPH-01/02
were harness-refuted (true negatives); SOPH-04/05/06/07 were blocked/not-promoted and none is awarded.

## Misses (4 of 5 awarded; bounded 8-surface first hunt)
- **001-M** `setStartBlock` not updating existing pools' `lastRewardBlock`. Failure mode = **examined-but-rejected**:
  the sf-07 subagent saw `setStartBlock` but rejected it ("reverts FarmingIsStarted once started"), missing the
  pre-start case. (Recurs the P198 FM-2 wrong-layer rejection pattern.)
- **002-M** `depositEth`→weETH treats eETH **shares** as amount. Failure mode = **examined-but-rejected**: sf-05 looked
  at `_eethTOweEth` and called it "exact". This is the **eETH analogue of my SOPH-03 stETH HIT** — I caught the stETH
  share-rounding revert but not the eETH share-vs-amount miscount on the same conversion family.
- **004-M** empty pool eats other pools' allocation (lpSupply==0 keeps allocPoint in totalAllocPoint). Adjacent to my
  SOPH-04 dilution theme but a different mechanism; not surfaced.
- **005-M** missing referral account on ETH deposits (lost referral rewards). Out of the surfaced attack surface
  (no missed-value/integration-referral lens in the 8-surface sample).

## Lessons
1. **Severity floor:** add a permanent-core-DoS → can-be-High carve-out (003-H under-rate).
2. **Conversion-family coverage:** when one share-rounding variant hits (stETH), force-check ALL siblings (eETH/sDAI)
   — would have converted the 002-M near-miss. (A sibling-parity lens, cf. the research detector platform.)
3. **Bounded sample = limited recall:** 8 surfaces caught the top High but missed 4 Mediums; a fuller sweep (or the
   coverage-manifest gate) is needed before claiming recall.
