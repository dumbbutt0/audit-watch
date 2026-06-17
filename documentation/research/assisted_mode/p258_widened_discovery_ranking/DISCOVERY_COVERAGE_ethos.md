# ethos — Phase 4: Discovery coverage (PRE-REVEAL, FROZEN)

## E-L1 ActivePool._rebalance
- top-5: E2 (B ERC4626 convexity), E3 (E withdraw-rounding desync), E1 (A profit recalc), E5 (A distribute-before-settle), E4 (G drift).
- strongest per family: A=E1/E5, B=E2, E=E3, G=E4. Empty: C, D, F.
- deserve ranking: E2, E3, E1, E5.

## E-L2 StabilityPool.offset
- top-5: E2 (G scale/epoch drift), E3 (B tiny-pool convexity), E1 (A rounding).
- strongest per family: A=E1, G=E2, B=E3. Empty: C, D, E, F.
- deserve ranking: E2, E3.

## E-L3 RedemptionHelper/SortedTroves
- top-5: E2 (C reInsert mis-sort), E3 (F cross-collateral identity), E4 (G base-rate), E1 (A fee).
- strongest per family: A=E1, C=E2, F=E3, G=E4. Empty: B, D, E.
- deserve ranking: E2, E3, E4.

**Family coverage note:** ethos spans A/B/C/E/F/G broadly (only D reentrancy sparse — Liquity is CEI-disciplined).
Widened enumeration added B (ERC4626 convexity), E (conversion), C (sorted-troves), F (cross-collateral) candidates
that an accounting-only pass would miss. **FREEZE.**
