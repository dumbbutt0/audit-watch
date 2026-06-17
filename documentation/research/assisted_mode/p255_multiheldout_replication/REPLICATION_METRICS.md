# P255 — Replication metrics (cross-contest, pooled with P254)

## Per-contest
| contest | loci | AWARDED_EQUIV | PARTIAL | SAME_AREA_WRONG_MECH | BENIGN | severe FP | proc-completed-not-base recoveries |
|---|---|---|---|---|---|---|---|
| **basin** (AMM math) | 3 | 2 (L1 High, L2 Med) | 0 | 0 | 1 | 0 | **2** |
| **bakerfi** (leverage vault) | 3 | 0 | 0 | 1 (L5) | 2 | 0 | **0** |
| **P255 total** | 6 | 2 | 0 | 1 | 3 | 0 | **2** |

## Mechanism-selection (the four required labels)
| label | basin | bakerfi | P255 |
|---|---|---|---|
| awarded-mechanism-selected | 2 (L1,L2) | 0 | **2** |
| awarded-mechanism-visible-but-not-selected | 0 | 1 (L5 fee) | **1** |
| awarded-mechanism-enumerated-then-refuted-incorrectly | 0 | 0 | **0** |
| awarded-mechanism-not-enumerated | 1 (L3 n/a) | 2 (L4,L6 n/a) | 3 |

**Awarded-mechanism-selection rate on loci that HAVE an awarded mechanism at the locus:** basin 2/2, bakerfi 0/1
→ **P255 pooled 2/3 ≈ 67%** vs **LoopFi 1/4 = 25%**.

## Pooled with P254 (n = 3 contests)
- Procedure-completed-not-base recoveries: LoopFi 1 (High) + basin 2 (1 High, 1 Med) = **3 total** (2 High, 1 Med).
- Severe false positives across all 10 loci: **0**.
- Awarded-mechanism-selection on awarded-loci: LoopFi 1/4 + basin 2/2 + bakerfi 0/1 = **3/7 ≈ 43%**.

## Primary question — does the routine *repeatedly* produce procedure-completed-not-base recoveries?
**Yes, numerically:** 2 more in P255 (both in basin), 3 across P254+P255. The recovery is **not** a pure one-off.

## Secondary question — is the main failure mode still mechanism selection?
**Yes, on the hard contest.** bakerfi L5 reproduced the LoopFi pattern exactly: routine engaged the awarded
function, saw an anomaly, but completed the **wrong** mechanism (P&L gap) and missed the awarded one (flash-loan
fee omission) though it was visible. Selection only "improved" where the bug-class was *mechanical/single-
mechanism* (basin's copy-paste typo and missing-revert), where there is essentially nothing to select.

## The confound that decides A vs B
The headline selection improvement (2/3 vs 1/4) is **driven entirely by basin's mechanical bug-class**, not by
better selection on subtle bugs. On the like-for-like subtle-accounting class (bakerfi L5; LoopFi L1/L3/L4),
selection is **still failing**. So replication is **real but bug-class-dependent**: the routine reliably completes
*impact* on math/typo bugs the base already nearly births, and still mis-selects the mechanism on subtle
accounting/state bugs — which is where the human-judge completion gap (P253) actually lives.
