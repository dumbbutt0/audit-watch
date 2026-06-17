# astaria — Phase 5: Ranking ablation (PRE-REVEAL, FROZEN)

Rank the deserve-ranking mechanisms under Profile A (P256 8-dim), B (messy-reconciliation weighted), C (runner-up
challenge). Per locus: A/B/C winners, top-2 per profile, why winner beat runner-up, falsifier.

## A-L1 (candidates A2 C-epoch, A3 D-reentrancy, A4 G-slope, A1 A-rounding)
- **Profile A winner: A4 (G slope/_accrue stale)** — clean, formula-shaped, high award-likeness/simplicity. top-2: A4, A1.
- **Profile B winner: A2 (C epoch advanced with unsettled withdrawProxy)** — state-machine terminality + cross-epoch
  reconciliation score highest under B. top-2: A2, A3.
- **Profile C winner: A2** — A's top (A4) vs runner-up: A2 has larger/more-terminal delta (stranded LPs), clearer
  victim, better award explanation; overtakes A4. top-2: A2, A4.
- why/falsifier: A2 wins on terminality+victim; falsifier = a settle-guard blocks epoch advance.

## A-L2 (A2 G-stale, A3 F-payee, A1 A-mismatch)
- **Profile A winner: A1 (A interest-mismatch)** — tidy accounting. top-2: A1, A2.
- **Profile B winner: A2 (G stale accrual at buyout)** — delayed-accrual drift upweighted. top-2: A2, A3.
- **Profile C winner: A3 (F wrong-payee identity)** — runner-up challenge: identity mismatch has the clearest
  victim/gainer + scalable theft → overtakes A1. top-2: A3, A2.
- why/falsifier: B and C **diverge here** (B=A2 temporal, C=A3 identity); falsifier A2 = accrue-on-buyout; A3 = payee enforced.

## A-L3 (A2 C-future-epoch, A3 B-convexity, A1 A-rounding)
- **Profile A winner: A1 (A rounding)** — tidy. top-2: A1, A3.
- **Profile B winner: A2 (C future-epoch double-count)** — state terminality. top-2: A2, A3.
- **Profile C winner: A2** — larger terminal delta than convexity. top-2: A2, A3.
- falsifier: per-epoch reserve isolation.

## Ablation summary
| locus | Profile A | Profile B | Profile C | B==C? |
|---|---|---|---|---|
| A-L1 | A4 (G slope, tidy) | A2 (C epoch) | A2 (C epoch) | yes |
| A-L2 | A1 (A tidy) | A2 (G stale) | A3 (F payee) | **no (B≠C)** |
| A-L3 | A1 (A tidy) | A2 (C future-epoch) | A2 (C future-epoch) | yes |

Pattern: A picks tidy every locus; B/C pick messier C/G/F. **A-L2 separates B from C** (B=temporal, C=identity).
**FREEZE.**
