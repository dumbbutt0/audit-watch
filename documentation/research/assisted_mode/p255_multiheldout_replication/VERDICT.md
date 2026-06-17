# P255 — VERDICT

## B — PARTIAL_REPLICATION

### What happened
The unchanged P254 five-operation routine was run blind (freeze-before-reveal) on 2 more unseen contests
(basin = AMM math; bakerfi = leverage vault). Result: **basin produced 2 procedure-completed-not-base recoveries**
— L1 `decodeWellData` (awarded **High #17**) and L2 `calcReserveAtRatio` silent non-convergence (awarded Medium),
both `awarded-mechanism-selected`, 0 severe FP. **bakerfi produced 0** clean recoveries: L5 reproduced the LoopFi
failure (engaged the awarded `harvest` function, saw the `deltaDebt` anomaly, but completed the **wrong** mechanism
— the P&L-conditional — and missed the awarded **flash-loan-fee omission** that was visible in scope); L4/L6 were
correct benign restraints. Pooled with P254: **3 procedure-completed-not-base recoveries (2 High, 1 Med), 0 severe
FP across 10 loci**.

### Why B and not A — even though the numeric A-bar is met
The stated A-bar (≥2 more recoveries, low severe-FP, selection better than LoopFi's 1/4) is **numerically
satisfied** (2 recoveries, 0 FP, P255 selection 2/3 vs 1/4). That is a genuine positive and is reported as such —
the recovery is **not** a one-off; it replicated. But two qualitative facts make a scaffold build premature:

1. **The recoveries are concentrated and bug-class-confounded.** Both P255 recoveries are in **one** contest
   (basin) and are **mechanical/math bugs** (a copy-paste typo; a missing revert) — a class where the base read
   already births ~most of the candidate and where there is essentially a *single* mechanism to "select." The
   improved selection rate (2/3 vs 1/4) is an **artifact of bug-class difficulty**, not evidence of better
   selection on the subtle bugs where the gap lives.
2. **The architecturally-realistic, subtle-accounting target (bakerfi) reproduced the failure.** L5 is the
   LoopFi pattern again: right function, real anomaly seen, **wrong mechanism completed**, awarded mechanism
   visible-but-not-selected. So the **secondary question's answer is "yes — mechanism selection is still the main
   failure mode" on hard targets**, which is exactly where a scaffold would need to add value.

So: replication is **real but uneven** — the routine reliably completes *impact* on math/typo bugs the base
nearly births, and still mis-selects the mechanism on subtle accounting/state bugs. That is "useful partials / a
couple more (thin-margin) recoveries," i.e. **B**, not the robust cross-architecture replication that justifies
committing engineering to a scaffold.

### Not A, not C, not D
- **Not A:** the recoveries are thin-margin and clustered in an easy bug-class; the hard contest still failed on
  mechanism-selection → building the scaffold now would optimize for bugs the base already finds while inheriting
  the unsolved selection gap.
- **Not C:** P254's recovery clearly **did** replicate (2 more, incl. a High) — it is not a one-off.
- **Not D:** the operations work (they completed 3 awarded chains total, 0 severe FP, and correctly refuted/
  restrained 5 non-awarded loci) — the op set is sound; **mechanism-selection**, not the operations, is the gap.

### Required next step before a scaffold build
Run one more held-out round **deliberately targeting the subtle-accounting / state bug-class** (not math/typo
bugs) across ≥2 diverse contests — i.e. test selection *where it actually fails*. Build the scaffold only if the
routine produces procedure-completed-not-base recoveries **on subtle bugs** with awarded-mechanism-selection
materially above the ~0/2 it currently shows there (bakerfi L5, LoopFi L1/L3/L4). If selection stays low on
subtle bugs, the binding constraint is **mechanism-discovery** (a training/tooling problem), and a chain-
completion scaffold will not close it.

### Honest caveats
n = 3 contests total; no PoCs (matches are by root-cause/impact equivalence to the awarded issues, not executed
exploits); reveals were post-freeze WebFetch/WebSearch of the C4 findings repos (no local keys existed); same-
operator confound (credited signal = procedure-completed-not-base delta). Per instruction, **no softening toward
A** — the numeric bar is acknowledged as met, and B is chosen on the bug-class confound + the reproduced hard-case
failure.

### Arc
P252(B observe≠complete) → P253(B 5 recurring ops, prove blind) → P254(B first blind completion, 1/4 selection) →
**P255(B replication real but bug-class-confined: 2 more recoveries on mechanical bugs, but the subtle-accounting
contest reproduced the mechanism-selection failure → test selection on subtle bugs before building).**
