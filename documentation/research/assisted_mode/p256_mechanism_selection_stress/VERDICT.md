# P256 — VERDICT

## B — SELECTION_PROMISING_NEEDS_MORE_HELDOUT

### What happened
A pre-completion **Mechanism Selection Gate** (8-dimension scoring over ≥3 enumerated mechanisms per locus) was
added ahead of the unchanged five completion ops, run blind (freeze-before-reveal) on subtle-accounting/state loci
only. **plaza** was fully revealed (3 scored loci); **concrete**'s awarded findings were **not publicly
retrievable** (404 report + private findings repo), so its frozen gate outputs remain **un-scored** → the
diagnosis rests on plaza alone.

plaza scorecard (n=3): **0 COMPLETED_CORRECTLY**, 0 RANKED_HIGH_BUT_NOT_COMPLETED, **2 ENUMERATED_BUT_RANKED_TOO_
LOW** (P-L2 fee = clean: awarded "large-redeems-reduce-collectible-fees" #714/#761 was the gate's **runner-up**;
P-L1 ≤1.2 pricing = region-level: the awarded split-deposit branch #756 was the **runner-up** region), **1
NOT_ENUMERATED** (P-L3 auction state-machine: endAuction-DoS / premature-undersold).

### Why B (not A/C/D/E/F)
- **The encouraging result:** the gate's enumeration **surfaced the awarded mechanism into the top-2 in 2/3
  loci** — clearly better than P255 blind selection (1/4, 0/1, with no runner-up tracking). So the 8-dimension
  enumeration *adds real recall of the awarded mechanism into the candidate set*.
- **But not solved:** in both of those the gate **ranked the wrong mechanism #1** → **selected-and-correct = 0/3**,
  and **0 COMPLETED_CORRECTLY**. So **not A** (selection is not solved/build-ready).
- **The dominant identifiable failure is ranking** (2/2 enumerated cases ranked-too-low) — which would point to
  **D (RANKING_GAP)**. **But** P-L3 was a pure discovery miss and P-L1's exact exploit was a discovery refinement,
  so discovery cannot be ruled out (**not cleanly D, not cleanly C**); the evidence **splits** ranking/discovery.
- **Completion is not the bottleneck** (0 RANKED_HIGH_BUT_NOT_COMPLETED → **not E**), consistent with P254/P255.
- **Not F:** the gate demonstrably helped (top-2 recall up vs P255).
- **Decisive limitation:** only **1 contest** was scored (concrete unavailable), so declaring a single dominant
  gap (C or D) on 3 loci would over-claim. Hence **B — promising, needs more heldout** to disambiguate.

### Leading hypothesis (to be confirmed, not built yet)
A **mechanism-ranking harness** is the leading candidate: the awarded mechanism was reachable in the gate's top-2
in 2/3 loci, so the binding constraint *when the mechanism is enumerated* is ranking, not discovery or completion.
The 8 gate dimensions over-weighted "comparand/award-likeness" toward tidy basis-mismatch mechanisms (P-L1 M1,
P-L2 M2) and under-weighted the messier-but-awarded reconciliation/convexity mechanisms (the runner-ups).

### Required next step
Confirmation run of the **same gate** on **≥1 more fully-revealed subtle contest** (verify the report is publicly
retrievable *before* committing — a P256 lesson: vet reveal-availability at target-selection time). Then:
- if `ENUMERATED_BUT_RANKED_TOO_LOW` recurs as dominant → build the **mechanism-ranking harness** (re-weight the
  gate dims; the awarded mechanism is usually the *less tidy* runner-up).
- if `NOT_ENUMERATED` recurs as dominant → build a **mechanism-discovery harness** (esp. state-machine / convexity
  bug shapes the current enumeration misses).
- only if `COMPLETED_CORRECTLY` reaches ≥2 → revisit A.

### Honest caveats
1 contest scored (concrete reveal unavailable); n=3 loci; no PoCs (classification by root-cause/impact match to
the published Sherlock issues); same-operator confound; P-L1 RANKED_TOO_LOW is region-level (runner-up named the
branch but not the exact exploit). Per instruction, **no softening** — 0 COMPLETED_CORRECTLY is reported plainly,
the gate's top-2 improvement is reported as promising-not-solved.

### Arc
P253(B 5 ops) → P254(B first blind completion, 1/4 selection) → P255(B replication real but bug-class-confined;
subtle-bug mechanism-selection still failed) → **P256(B mechanism-gate raises awarded mechanism into top-2 (2/3)
but ranks wrong #1 (0/3 selected, 0 completed); failure splits ranking/discovery; confirm on another fully-
revealed subtle contest, then build the ranking harness).**
