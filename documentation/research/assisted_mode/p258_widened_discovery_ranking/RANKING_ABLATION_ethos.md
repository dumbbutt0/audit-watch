# ethos — Phase 5: Ranking ablation (PRE-REVEAL, FROZEN)

## E-L1 (E2 B-convexity, E3 E-rounding, E1 A-recalc, E5 A-distribute)
- **Profile A winner: E1 (A profit recalc mismatch)** — tidy accounting basis. top-2: E1, E5.
- **Profile B winner: E2 (B ERC4626 convexity / share-price manip)** — convexity + insolvency upweighted. top-2: E2, E3.
- **Profile C winner: E2** — runner-up challenge: E2 has largest terminal delta (drain via share-price) + scalable; overtakes E1. top-2: E2, E1.
- why/falsifier: E2 wins terminality/amp; falsifier = yield vault inflation-safe.

## E-L2 (E2 G-scale-drift, E3 B-tiny-pool, E1 A-rounding)
- **Profile A winner: E1 (A rounding)** — tidy. top-2: E1, E2.
- **Profile B winner: E2 (G scale/epoch drift)** — delayed/epoch drift upweighted. top-2: E2, E3.
- **Profile C winner: E2** — bigger cumulative depositor delta than tiny-pool. top-2: E2, E3.
- falsifier: scale/epoch handling matches Liquity reference.

## E-L3 (E2 C-reInsert, E3 F-cross-collateral, E4 G-base-rate)
- **Profile A winner: E4 (G base-rate)** — formula-shaped/tidy. top-2: E4, E1.
- **Profile B winner: E2 (C reInsert mis-sort)** — state-machine terminality upweighted. top-2: E2, E3.
- **Profile C winner: E3 (F cross-collateral identity)** — runner-up challenge: identity/cross-collateral has
  clearest victim + scalable theft; overtakes. top-2: E3, E2.
- why/falsifier: B and C **diverge** (B=C-state, C=F-identity); falsifier E2 = reInsert recomputes NICR; E3 = per-collateral binding.

## Ablation summary
| locus | Profile A | Profile B | Profile C | B==C? |
|---|---|---|---|---|
| E-L1 | E1 (A tidy) | E2 (B convexity) | E2 (B convexity) | yes |
| E-L2 | E1 (A tidy) | E2 (G scale-drift) | E2 (G scale-drift) | yes |
| E-L3 | E4 (G tidy) | E2 (C reInsert) | E3 (F identity) | **no (B≠C)** |

Pattern: A picks tidy; B/C pick messy. **E-L3 separates B (state-machine) from C (identity).** **FREEZE.**
