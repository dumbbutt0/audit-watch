# hybra — Phase 5: Ranking ablation (PRE-REVEAL, FROZEN)
Profiles A (P256 8-dim), B (messy-reconciliation), C (runner-up challenge).
## H-L1 (T8 inflation, M1 desync, M2 dust)
- Profile A winner: **M2 (rounding dust)** — tidy/quantifiable; top-2: M2, M1.
- Profile B winner: **M1 (permanentLockBalance desync)** — global-invariant reconciliation upweighted; top-2: M1, T8.
- Profile C winner: **T8 (voting-power inflation round-trip)** — runner-up challenge: largest/most-terminal delta
  (mint voting power), scalable, best award explanation; overtakes; top-2: T8, M1.
- B≠C (B=desync, C=inflation). falsifier T8: split+merge conserves voting power exactly.
## H-L2 (M1 permanent edge, T6 round-trip)
- A: M1 (tidy). B: M1 (reconciliation). C: T6 (round-trip drift). top-2 each as noted. B≠C.
## H-L3 (M1 double-count, T6 drift, T1 DoS)
- A: M1 (tidy accounting). B: M1. C: T1 (DoS) or T6. top-2: M1,T6.
## Summary
| locus | A | B | C |
|---|---|---|---|
| H-L1 | M2 dust (tidy) | M1 desync | **T8 inflation (Pass2)** |
| H-L2 | M1 | M1 | T6 (Pass2) |
| H-L3 | M1 | M1 | T1/T6 (Pass2) |
Note: Profile C repeatedly elevates **Pass-2-generated** mechanisms (T8/T6/T1). **FREEZE.**
