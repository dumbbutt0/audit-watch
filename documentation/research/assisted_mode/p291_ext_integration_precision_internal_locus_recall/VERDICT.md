# P291 — VERDICT

## Verdict: **B — EXT_PRECISION_INTERNAL_RECALL_PROMISING_NEEDS_REFINEMENT**

## Core question
Can we remove generic EXTERNAL_INTEGRATION false READYs AND surface internal reward/accounting loci, without increasing
false READYs or severe FP? **Part A: yes, fully. Part B: surfacing yes, end-to-end no** (the surfaced internal locus is
dropped by the coverage router's duplicate-class dedup before Lens 3) → one side complete, the other needs a
coverage/queue refinement → **B**.

## Scorecard
| criterion | result |
|---|---|
| Pools.deposit no longer READY | ✔ NEEDS_INTEGRATION_DEVIATION_EVIDENCE |
| no generic EXTERNAL_INTEGRATION READY remains | ✔ (0 corpus-wide) |
| no false READY introduced | ✔ |
| `_increaseUserShare`-style internal locus surfaced | ✔ (advisory layer) — **but dedup-blocked before Lens 3** |
| internal-locus expansion bounded | ✔ (≤3/entry, ≤15/contest, advisory_only) |
| severe concluded/reportable FP = 0 | ✔ |
| regressions kelp H-01 / blackhole claim_many / L2Governor / ECG H-04 preserved | ✔ (all READY) |
| tests green | ✔ (346 P260–P290 + P291) |

## Why B not A
Part A is verdict-A-quality on its own (the P290 false READY is eliminated, fail-closed, 0 FP). Part B repairs the
LITERAL recall gap (the awarded internal locus now exists in the candidate set, generically + bounded + FP-safe) but the
END goal — Lens 3 firing on the reward-index bug — is blocked by the P273 `COVERAGE_DEFER_DUPLICATE_CLASS` dedup, a
distinct localized blocker at a layer P291 may not edit. Honest "one side repaired, the other needs refinement" = B.

## Net effect
- The P290 false-READY class is closed: EXTERNAL_INTEGRATION can no longer reach READY on a class-template hypothesis;
  it requires a concrete source-backed deviation (auto low-level/callback/reentrancy-ordering or explicit structural).
- Internal accounting/reward/share/index loci (incl. the awarded `_increaseUserShare`) are now surfaced from public
  entries — strictly more recall than P290, generically and bounded, with 0 FP.
- All key regressions preserved; severe FP = 0.

## Production authority
**WITHHELD.** Research/advisory only; reused modules imported read-only.

## Next
Land the coverage/queue refinement (P292): reserve a validation-queue slot for internal-locus candidates OR let a
distinct-locus same-class internal candidate past coverage duplicate-class dedup → so Lens 3 receives `_increaseUserShare`
and either lifts it or precisely blocks it. THEN re-blind a fourth target. Still NOT scaleout.
