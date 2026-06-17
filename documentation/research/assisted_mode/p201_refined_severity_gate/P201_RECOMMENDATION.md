# P201 — recommendation

## Final decision: `REFINED_GATE_PARTIAL` (non-oracle) — demotion validated, preservation untested

The refined **mechanism-level** severity gate was designed to fix P200's three failures (blanket oracle→High,
blanket precision→High, per-surface folding of a secondary High) and validated out-of-sample on a 2nd fresh sealed
corpus (zetachain-2023-10, 14H/34M). Result is a genuine but **one-sided** improvement.

### Validated ✓ (the demotion axis)
- **Over-HIGH on mechanism-matched awarded-Mediums: ceiling 6/7 → refined 0/7** (all fixed) — a large improvement
  over P200's 1/4. Every matched contract-Medium the ceiling over-rated (tx.origin/M-13, updateSystem-DoS/M-28,
  gas-limit/M-16, plus loose M-01/M-09/M-26/M-30) was calibrated to Medium/Harness.
- **The class rules generalize:** DoS/griefing → Medium; admin/TSS/owner-compromise (auth) → Medium (admin-prereq
  cap); permissionless-but-depends-on-unseen-code → Harness; precision/self-inflicted → Medium. P199's blanket-High
  failures do not recur.
- **Per-mechanism grading works:** all 46 carried mechanisms graded independently across 18 surfaces; the P200 H-02
  surface-folding failure is structurally eliminated.

### NOT validated ✗ (the preservation axis — the decisive gap)
- **High-preservation is UNTESTED.** 11/14 zetachain Highs are off-chain (observer/cctx/consensus, out of Solidity
  scope); the 3 contract-level Highs (H-06/H-10/H-13) were recall misses. **0 awarded-Highs were matched by
  mechanism** → the gate never had to preserve one.
- **0 HIGH_CONFIRMED across 46 mechanisms = no positive control.** Plausibly correct for zetachain's contract layer
  (its theft-Highs are off-chain), but we cannot rule out that the reject-first bar is **too aggressive**. The gate's
  High-*confirming* path is unexercised.

## Why PARTIAL (decision-space justification)
- Not `REFINED_GATE_VALIDATED`: preservation untested; a "validated" claim needs a positive control.
- Not `REFINED_GATE_FAILED_FALSE_DEMOTIONS`: **0** matched awarded-Highs were demoted (none were matched); every
  matched contract-Medium was handled correctly.
- Not `DATASET_TOO_THIN` outright: the corpus gave strong signal on the **demotion** axis (6/7 matched Mediums); it
  is "too thin" **only for the High-preservation axis** (0 matched Highs) — recorded as such.
- `ORACLE_PRECISION_FRONTIER_UNRESOLVED` is folded in as a standing caveat (oracle N/A here, precision light), but
  the headline is the demotion-vs-preservation split.

## Standing caveat (carried, per user direction)
**Oracle severity remains UNVALIDATED_OUT_OF_SAMPLE.** No fresh sealed corpus has oracle surfaces; the oracle branch
(class B) is design-only. Do not claim it production-validated. → **P202** (oracle-rich corpus search) → **P203**
(oracle gate validation).

## Recommended next (each needs explicit go — NOT actioned here)
1. **Do not wire the gate yet.** Demotion is validated twice (predy partial, zetachain strong) but High-preservation
   has *never* been validated out-of-sample (predy: 1 matched High under-graded; zetachain: 0 matched Highs).
2. **Positive-control corpus is now the critical need:** a fresh sealed corpus with **permissionless contract-level
   Highs** (direct theft/insolvency in Solidity) to prove the gate **confirms** genuine Highs, not just demotes
   non-Highs. Candidates to screen: decent (4H, bridge), munchables (2H, auth), vultisig (3H) — but each must be
   checked for *contract-level* (not off-chain) Highs before use. This is distinct from P202's oracle search.
3. **Keep the refined gate design** (`REFINED_SEVERITY_GATE_DESIGN.md`): per-mechanism + the A–F class rules. The
   admin-prereq→Medium and unseen-dependency→Harness rules are the workhorses and generalized cleanly.
4. Recall misses (H-06/H-10/H-13) are a **deep-pass coverage/recall** matter (P183–P188 frontier), separate from the
   severity gate; H-10 specifically was a sampling gap (Trident not sampled).

## Acceptance criteria — met
No production changes ✓ · fresh corpus ✓ · count-only unseal before blind run ✓ · double freeze before answer-key
read (`77d57371`/`387a95de`) ✓ · gate applied offline/read-only only, not implemented ✓ · original vs refined scored
separately ✓ · **mechanism-level** scoring (not only surface) ✓ · secondary-High preservation machinery exercised
(46 mechanisms) ✓ · P200 oracle/precision failures addressed in design (oracle carved out, precision magnitude-
dependent) ✓ · production hashes byte-identical START==END ✓ · JSON valid ✓ · `fabrication_rate=0` ✓.
