# P250 — Metrics (the six requested)

Forward blind run, frozen post-P249 system (P245 gate + accounting checkpoint ENABLED; no state-transition
checkpoint), target spectra-2024-02 (unseen). Awarded: 0 High + 2 Medium (denom 2 weighted).

| # | Metric | Value | Note |
|---|---|---|---|
| 1 | **Accounting candidates born** | reinforced 4 base loci (B-1,B-2,B-3,B-5); **0 NEW** beyond base | checkpoint fired at every base accounting locus; base hunt already birthed them |
| 2 | **Accounting exploit chains completed** | **0 new** (4 reinforced chains already in base) | none constructed that the base lacked |
| 3 | **Question volume** | **29** question-records (A1×17, A2×6, A5×3, A3×2, A4×1) | bounded; small contest (vs 89–125 in P249's larger ones) |
| 4 | **Time overhead** | checkpoint compute **0.066 s**; answering 29 questions ≈ a few operator-minutes | negligible compute; modest reasoning overhead |
| 5 | **Recall lift** | **0.0** (base 25% credited → +checkpoint 25%; strict 0%→0%) | no awarded finding recovered only via the checkpoint |
| 6 | **FP / noise** | **0 findings emitted, 0 conclusions, 0 high-confidence FP**; ~25/29 benign records resolved to no-candidate; non-accounting code fired nothing | invariant re-verified on the unseen target |

## Reading
- **Architecture generalized (confound-light signals):** on a target it was never tuned on, the checkpoint
  fired only on real accounting loci, emitted 0 findings / 0 conclusions / 0 FP, cost 0.066 s, and produced a
  bounded 29 question-records. It did not behave like a detector.
- **Recall lift was 0 — by contest composition, not failure:** spectra's two awards are permission (M-01) and
  cross-contract (M-02), neither accounting-family. The checkpoint correctly added no accounting candidate
  where none was warranted (precision win) and reinforced the M-02 locus without completing its cross-contract
  chain.
- **Confound note:** spectra is public (training exposure possible) → the base 25% is an upper bound; the
  checkpoint-attributable delta (0) is confound-light and the robust result.
