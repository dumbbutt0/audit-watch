# astaria — Phase 4: Discovery coverage (PRE-REVEAL, FROZEN)

Forces broad discovery before narrow ranking. Per locus: top-5, strongest-per-family, empty families, ranking set.

## A-L1
- top-5: A2 (C epoch-unsettled), A3 (D reentrancy), A4 (G slope-stale), A1 (A rounding), + (B convexity: n/a here).
- strongest per family: A=A1, C=A2, D=A3, G=A4. Empty: B (no nonlinear payoff here), E (no migration), F (no identity).
- deserve ranking: A2, A3, A4 (A1 dust).

## A-L2
- top-5: A2 (G stale-accrual), A3 (F wrong-payee), A1 (A interest-mismatch), A4 (D reentrancy).
- strongest per family: A=A1, G=A2, F=A3, D=A4. Empty: B, C, E.
- deserve ranking: A2, A3, A1.

## A-L3
- top-5: A2 (C future-epoch double-count), A3 (B across-epoch convexity), A1 (A rounding).
- strongest per family: A=A1, C=A2, B=A3. Empty: D, E, F, G.
- deserve ranking: A2, A3.

**Family coverage note:** astaria's subtle surface concentrates in A/C/D/G (epoch state-machine + temporal slope +
reentrancy); B sparse, E/F mostly empty. Widened enumeration added C/D/G candidates the P256/P257 accounting-only
pass would have missed. **FREEZE.**
