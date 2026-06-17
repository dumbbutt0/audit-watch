# P250 — Checkpoint Pass — FROZEN pre-reveal

Base freeze hash: 5ab782d31f3c526e68392bfeb07bc4cb24afd2eb736fa4365eaf2f6aa22d40e0.
Ran `accounting_checkpoint_audit.py --manifest <spectra> --out outputs/spectra_checkpoint.json`. Invariant
re-verified: `emits_findings:false`, `concludes_vulnerability:false`, **0 records carry a conclusion**.
Checkpoint compute time: **0.066 s**. Question-records: **29** (A1 rounding 17 · A2 conservation 6 · A5 index
3 · A3 double-count 2 · A4 shared-balance 1).

## Loci flagged (the checkpoint observed the real accounting surface)
`_convertIBTsToSharesPreview` (A1) · `_withdrawShares` (A1/A2) · `_depositIBT` (A1/A2/A3) · `_computeYield`
(A1) · `_convertToAssetsWithRate` / `_convertToSharesWithRate` (A1) · `storeRatesAtExpiry` (A1) · `flashLoan`
(A3/A4) · plus conversion getters.

## Answering the 6 questions per locus → constructed candidates
| Locus (family) | Q answers → result | maps to base? | NEW? |
|---|---|---|---|
| _convertIBTsToSharesPreview (A1) | Q5 rounding wrong side? YES — preview rounds shares UP vs deposit DOWN | = **B-1** | no |
| _computeYield (A1) | Q1/Q2/Q3 — depeg Floor/Ceil + SAFETY_BOUND dust may over/under-attribute yield | = **B-5** | no |
| storeRatesAtExpiry (A1) | Q6 repeat/timing — first-call snapshot front-runnable | = **B-2** | no |
| flashLoan (A3/A4) | Q4 deprive others? lends entire IBT incl. user-backing | = **B-3** | no |
| _withdrawShares (A1/A2) | Q5 — shares burned with `Ceil` (favors protocol) → correct direction | benign | no |
| _depositIBT (A2/A3) | Q1–Q3 — fee to unclaimed+total are separate accumulators; conserved | benign | no |
| _convertToAssetsWithRate / WithRate (A1) | helper rounding follows caller intent | benign | no |
| ~21 other accounting records | answers resolve to "no value created/destroyed/double-counted/deprived/mis-rounded" | benign | no |

## Result
- The checkpoint **fired at every base accounting locus** and, when its six questions were answered,
  reinforced base candidates **B-1, B-2, B-3, B-5** at the correct loci.
- **NEW candidates beyond the base hunt: 0.** On this small, carefully-read contest the base hunt already
  birthed the accounting candidates the checkpoint would force.
- Benign question-records (~25 of 29) resolved to no-candidate. 0 findings emitted, 0 conclusions.

FREEZE: checkpoint-pass results above are final pre-reveal.
