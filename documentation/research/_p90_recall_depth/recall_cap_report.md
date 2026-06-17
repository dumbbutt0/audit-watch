# P90-A — Recall cap analysis (P81e / P85 / P87 / P89)

Reconstructed from each phase's **full lens-surfaced lead list** (re-run deterministically, lens hash
`29a7b915`) + a curated awarded→entry-function map (sourced from the findings reports + each phase's
`scores.json`). Data: `recall_cap_table.json`. **Historical scores unchanged.**

## Surface recall @ cap (awarded findings whose entry-function is within the top-N lens ranks)
| Phase | lens total | selected (used) | awarded H/M | @8 | @12 | @16 | @20 | @full |
|---|---|---|---|---|---|---|---|---|
| P81e (vultisig) | 36 | 12 | 6 | 0/6 | 4/6 | 4/6 | **5/6** | 5/6 |
| P85 (munchables) | 8 | 8 (all) | 6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| P87 (traitforge) | 54 | 11 | 25 | 6/25 | 13/25 | 13/25 | 13/25 | **17/25** |
| P89 (phi) | 67 | 11 | 15 | 5/15 | 6/15 | 6/15 | 6/15 | 6/15 |

## Newly-captured awarded surfaces ABOVE the cap actually used (the marginal value of a bigger cap)
| Phase | →16 | →20 | →full | extra investigations for "full" |
|---|---|---|---|---|
| P81e | +0 | **+1** (M-03 `buy` @19) | +1 | +24 |
| P85 | +0 | +0 | +0 | 0 |
| P87 | +0 | +0 | **+4** (EntropyGenerator `initializeAlphaIndices`/`getNextEntropy`/`writeEntropyBatch` + `burn`) | +43 |
| P89 | +0 | +0 | +0 | +56 |

## Miss categories (aggregate across the 4 phases)
| Category | Count | Cap-addressable? |
|---|---|---|
| **rejected** (selected, deep-pass rejected) | **21** | No — DEPTH |
| **unsurfaced_internal** (internal helper / negative space / low-scoring unselected contract) | **17** | No — lens limitation |
| **below_cutoff** (surfaced, ranked below the cap used) | **5** | Partly — only at near-full cap |
| converted (CLEAN/STRONG/matched) | 7 | — |
| not_run (selected, not investigated — budget) | 1 | No — THROUGHPUT |
| unsurfaced_missing (missing function) | 1 | No — negative space |

## Findings
1. **Raising the global lead cap is low-value in this corpus.** Going from the cap actually used (8–12) to
   **top-16 or top-20 captures ZERO additional awarded surfaces in 3 of 4 phases** (P85/P87/P89) and only +1 in
   P81e (the `buy` lead at rank 19, caught at top-20). The +4 in P87 appears only at ~full (54) — uneconomical
   (+43 investigations for 4 surfaces, most of which would still need deep conversion).
2. **The misses are overwhelmingly DEPTH and NEGATIVE-SPACE, not cap.** `rejected` (21) + `unsurfaced_internal`
   (17) = 38 of the 45 non-converted awarded findings. A wider cap touches neither.
3. **The one cap-addressable pattern is low-scoring security-critical contracts.** P87's `EntropyGenerator`
   entrypoints scored 1 (ranks ≫20) so its 3 awarded findings (H-06/M-01/M-05) fell below cutoff — but a flat
   global cap only reaches them near full. A **per-contract floor** reaches them cheaply.
4. **`not_run` is throughput, not cap.** P89 H-01 (`signatureClaim`) was *selected* but not investigated
   (budget). Completing selected leads recovers it with no cap change.

## Recommendation — default lead-cap policy
- **Keep the global cap modest:** `top-12` for ≤2 in-scope contracts; `top-16` for larger multi-contract
  subjects. A flat raise beyond 16 is not justified by the data.
- **ADD a per-in-scope-contract floor:** always select the **top-2 leads per in-scope contract** (union with
  the global top-N). This is the highest-value cheap change — it covers security-critical but low-scoring
  contracts (the `EntropyGenerator` class: H-06/M-01/M-05) that a flat global cap misses, for only a handful of
  extra investigations.
- **Partial-completion rule:** prioritize **completing every SELECTED lead** (drive `NOT_RUN`→0) before
  widening the cap; a selected-but-NOT_RUN High (P89 H-01) is a pure throughput loss. If budget is tight,
  shrink the *global* cap but keep the per-contract floor, rather than selecting many leads and NOT_RUNning
  them.
- **Accept the residual:** `unsurfaced_internal` / negative-space (internal helpers, missing functions) is a
  lens limitation not solved by any cap. Partially mitigated by the P90-D taxonomy additions (index-integrity,
  signature-replay) and a future negative-space lens (deferred — single confirmed instance so far).

**Net:** the recall lever is **per-contract coverage + completing selected leads + conversion depth**, not a
bigger global cap. P91 should adopt `top-16 + per-contract top-2 floor + NOT_RUN→0` and measure conversion,
not just surface recall.
