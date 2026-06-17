# P259 — Diagnosis (target-fit vs locus vs discovery vs ranking vs completion)

## Scope
- Selected: hybra (clean), sentiment (disclosed-contaminated). Rejected: olas/recall (wrong-class) + the
  award-revealed/used/barred set (TARGET_FIT_SCREEN). Scored contests: 2 (1 clean + 1 asterisked).
- Reveal depth: **search-level-plus** (hybra headline + areas; sentiment per-issue areas) — deeper than P258 but
  the hybra findings-repo issue filter 404'd, so not exhaustive per-issue. Stated limitation.

## Confound removal (the point of P259)
- **Target-fit confound REMOVED:** unlike astaria (P258, mechanical/access-control awards), hybra + sentiment
  awards are **subtle_accounting_state** (hybra gHYBR first-depositor share-inflation; sentiment #613 bad-debt
  share-inflation). The award-class-fit screen **worked**. (Caveat: sentiment SuperPool awards #277/#510/#440 skew
  compliance/config — partial fit there.)
- **Reveal-depth confound PARTIALLY removed:** deeper than P258, but not full per-issue (hybra split/merge mechanisms unverified).

## Awarded-mechanism placement (confirmed)
| metric | value |
|---|---|
| full awarded count | hybra 10 (1H/9M); sentiment many (subset retrieved) |
| subtle_accounting_state awards | hybra ≥ (gHYBR + split/merge + reward); sentiment #613 bad-debt + others |
| in selected locus, cleanly SELECTED+COMPLETED pre-reveal | **0** |
| awarded mechanism whose SHAPE my Pass-2 generated | **≥2** (hybra gHYBR = T8; sentiment #613 = T8) |
| awarded mechanism missed by LOCUS selection | **hybra gHYBR (checkpoint-hit, not selected)** |
| awarded mechanism right-family-wrong-locus/rank | **sentiment #613 (T8 at S-L1 not S-L2)** |
| Pass-2 added shapes beyond Pass-1 families? | YES (T8 share-price, T7 solvency, T2 withdraw-coupling) |
| per-profile awarded-selected A/B/C | 0 / 0 / 0 (confirmed) ; severe FP 0 |

## The refinement vs P258
P258 concluded "discovery dominates; widening the family checklist didn't reach awards." P259, after removing the
target-fit confound and adding shape-generators, shows: **the Pass-2 shape vocabulary IS right** — it generated the
exact award classes (T8 share-price/inflation = both contests' headline subtle awards; T7 solvency = sentiment
bad-debt). The failure is **not "wrong shapes"** but **applying them at the wrong LOCUS**:
- hybra: the headline award's locus (`GrowthHYBR.deposit`) was a **checkpoint hit that locus-selection skipped**.
- sentiment: the matching shape (T8) was placed at S-L1, not at the awarded locus (S-L2 bad-debt).
⇒ **LOCUS_SELECTION is the newly-isolated leading gap**, with **ranking (B/C)** downstream (B/C did elevate the
right shape *families* when present). Pure mechanism-shape **discovery is largely solved by Pass-2**.

## Bottleneck (one)
**LOCUS_SELECTION_GAP.** Target-fit was fixed; Pass-2 shape discovery generated the awarded classes; but the
procedure failed to subject the award-carrying loci to that shape discovery (hybra) or to rank the shape at the
right locus (sentiment). Discovery-of-shapes is adequate; **discovery-of-which-locus is the gap**, ranking second.

## Honest caveats
n=2 (1 contaminated, asterisked); search-level-plus (not exhaustive per-issue); 0 clean SELECTED+COMPLETED →
below the build threshold; sentiment SuperPool awards partially mechanical/compliance (residual target-fit noise);
corpus exhausted (no more clean held-outs without acquiring fresh contests).
