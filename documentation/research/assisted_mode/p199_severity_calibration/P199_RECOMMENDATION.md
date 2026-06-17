# P199 — recommendation

## Final decision: `SEVERITY_FRONTIER_CONFIRMED`

The Medium-severity calibration failure (P198 FM-1) is **systematic across corpora**, measured **before** any fix:
- **88.9%** over-HIGH on the confound-free Medium/Low-awarded subset (8/9), with per-corpus rates of 100%
  (quantamm, panoptic, ark) and 66.7% (centrifuge mapped).
- **11/12** surfaces rated ≥HIGH on the controlled all-Medium / 0-High Centrifuge corpus.
- **29/30** blind verdicts are ≥HIGH; only **1** below-HIGH in the whole dataset.
- Confound excluded: **12/12** genuine-High surfaces (P189 High-sample) correctly ≥HIGH; **zero** false-LOW.

## What it is — and isn't (the honest reframe)
The blind `verdict` is a **worst-case threat ceiling** by `deep_trace.md` design, **not** a calibrated severity,
and there is **no calibration step** between them. So this is a **missing-gate** problem, not "the stack is wrong":
its *recall* (mechanism enumeration) is intact and generalizes (P189/P198); only the *severity grade* is
un-calibrated. The dominant case pattern is **griefing/DoS rated as theft** (4/8) and **unproven loss magnitude**
(3/8); the rest are local-loss-as-protocol-wide and compliance-as-insolvency.

## Discriminator (evidence-grounded, separates all 12 Highs from all 8 over-HIGH Mediums)
High requires a *proven, permissionless* path to **theft / insolvency / permanent loss / unauthorized privileged
transition**, of **material magnitude**, with no trusted prerequisite and no narrow timing dependency. DoS /
griefing / precision / compliance / bounded-local → Medium.

## Recommended next (each needs explicit go — NOT actioned here)
1. **Severity gate as a measured production change** (`SEVERITY_GATE_PROPOSAL.md`): a reject-first post-verdict
   calibration step. On this dataset it removes 8/8 over-HIGH with **0 genuine-High demotions** — but ship only
   after measuring on **fresh** corpora (the gate is currently fit on the same data it was derived from; same
   by-construction caveat as P187).
2. **Blind validation of the gate** before wiring (P186/P189-style): does the discriminator hold on a held-out
   corpus (badger/kleidi)? This is the honest precondition to any `deep_trace.md`/checker change.
3. Do **not** widen detectors or touch routing — the frontier is severity calibration, confirmed.

## FM-2 disposition
Wrapper/callee confusion appears in **1** over-HIGH case (centrifuge M-04) → recorded as a calibration **data
point**, not a recurring severity cause (per the spec). It remains a P198 recall/locus item, not a severity driver.

## Acceptance criteria — met
Entire phase read-only ✓ · no production prompt/tool/checker/severity edits ✓ · cross-corpus dataset from existing
artifacts only ✓ · over-HIGH measured before any fix proposed ✓ · Medium-vs-High evidence-grounded (not intuition) ✓
· FM-1 **confirmed systematic** ✓ · FM-2 included only as a data point ✓ · JSON valid ✓ · production hashes
byte-identical start→end ✓.
