# P290 — DIAGNOSIS

## Target: salty-2024-01-holdout (Salty.IO, C4 2024-01) · awarded H/M = 37 (6H/31M; 4 Highs in-scope, 2 removed)
Fresh, never scored (submit/poc=0); content-light H/M screen only; staking/rewards/pools domain (lens-fit by design).

## Funnel (blind, pre-reveal)
- advisory 22 · validation queue 10 (7 classes) · READY 1 · PoC-supported 0.
- **P289 lens firings: 0.** **STRONG/EXACT awarded recoveries: 0.**
- match levels: SUBSYSTEM_ONLY_RECALL 3 (H-02/H-04/H-05 contracts surfaced), MISSED 1 (H-01), OUT_OF_SCOPE 2 (H-03/H-06).
- **READY-layer false positive: 1** (Pools.deposit, EXTERNAL_INTEGRATION template; caught pre-reveal by PoC PASS_REFUTED).
- severe concluded/reportable FP: 0. non-awarded TP: 0.

## Two clean failures (both localized)
1. **READY precision miss (verdict driver)**: the frozen **P279 EXTERNAL_INTEGRATION template** lifted `Pools.deposit`
   to READY on the class label + a generic callback hypothesis, with invariant_delta NO_REFERENCE — i.e. WITHOUT a
   source-backed deviation. The function is `nonReentrant` with a plain `safeTransferFrom`; the PoC refuted the claim.
   → an EVIDENCE_DERIVATION/READY-precision gap for the EXTERNAL_INTEGRATION class (it should require a derived
   deviation, not a class-template hypothesis). Pre-existing P279 behavior, exposed blind.
2. **Lens starved by recall**: H-02/H-04 are reward-index/first-depositor bugs (Lens 3's exact class) on
   `StakingRewards._increaseUserShare`, but that internal locus was never surfaced (only `claimAllRewards` was queued), so
   Lens 3 had no candidate to fire on. → RECALL_GAP for internal accounting loci.

## Comparison to P287/P288/P289
- P287 (kelp): A — D4.6 oracle lens lifted awarded H-01.
- P288 (ECG): D — lens-bounded, strong recall, 0 READY.
- P289 (ECG supervised): A — loss-on-stake lens lifted awarded H-04, 0 FP.
- **P290 (salty blind): D — 1 unsupported READY (EXTERNAL_INTEGRATION over-claim, PoC-refuted), 0 lens firings, 0 awarded
  recovery.** The P289 lenses did NOT generalize here — partly recall-starved (awarded reward-index locus not surfaced),
  partly because the lenses are still narrow. Generalization remains partial/lens-and-recall-bounded.

## Final bottleneck (exactly one): **F — EVIDENCE_DERIVATION_GAP**
The verdict-D driver is the EXTERNAL_INTEGRATION template producing a READY without a source-backed deviation
(NO_REFERENCE) — a derivation/precision gap. Secondary (localized): RECALL_GAP on internal accounting loci
(`_increaseUserShare`) that starved the reward-index lens. Neither selection nor the READY gate's strictness is the issue.
