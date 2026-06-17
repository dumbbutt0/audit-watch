# P201 — original threat-ceiling vs refined mechanism-level calibration (zetachain-2023-10)

Scored separately. "Original" = blind `deep_trace.md` verdict (threat ceiling). "Refined" = the mechanism-level
6-class gate, frozen before the seal opened (`77d57371` / `387a95de`). Awarded: **14 High / 34 Medium**.

## Headline
| metric | original (ceiling) | refined (gate) |
|---|---|---|
| surfaces ≥ HIGH | **16 / 18 (88.9%)** | **0 / 18 HIGH_CONFIRMED** |
| per-mechanism labels (46 total) | — | 26 Medium · 18 Harness · 1 refuted · 1 insufficient · **0 High** |
| over-HIGH on mechanism-matched awarded-Medium | **6 / 7** | **0 / 7** (all 6 fixed) |
| genuine-High preservation (mechanism-matched) | n/a | **UNTESTED — 0 matched Highs** |
| false-demotion of a matched awarded-High | — | **0** (none to demote) |

## What this shows
1. **Ceiling skew reproduced a 3rd time:** 88.9% of surfaces ceil at HIGH on a corpus that is 34/48 Medium —
   confirming again that the deep-trace verdict is a threat ceiling, not a severity.
2. **The refined demotion rules generalize strongly.** On the contract-Medium findings the blind run actually
   matched, the ceiling over-rated 6/7 as ≥HIGH; the refined gate calibrated **all 6** to Medium/Harness →
   **0/7 over-HIGH**. This is a large improvement over P200's 1/4-fixed. The mechanisms demoted are exactly the
   classes the refinement targeted: **DoS/griefing → Medium**, **admin/TSS/owner-compromise (auth) → Medium**
   (admin-prereq cap), **permissionless-but-depends-on-unseen-code → Harness**, **precision/self-inflicted → Medium**.
3. **Per-mechanism grading works mechanically.** All 46 carried mechanisms got their own label across 18 surfaces;
   no surface label suppressed a sub-mechanism (the P200 H-02 folding failure does not recur structurally).

## What this does NOT show (the critical gaps)
1. **High-preservation is UNTESTED.** Of zetachain's 14 Highs, **11 are off-chain** (Go observer/cctx/consensus:
   NonceVoter, observer nodes, ballot voting, UTXOs, TSS-key voting, reorgs) — unreachable by a Solidity-source
   blind trace — and the **3 contract-level Highs** (H-06 zEVM message-ignored, H-10 Trident router-revert,
   H-13 pause-during-cctx) were **recall misses** (the blind run found different mechanisms, or the file wasn't
   sampled). So **0 awarded-Highs were matched by mechanism** → the gate's ability to *preserve* a genuine High
   was never exercised.
2. **0 HIGH_CONFIRMED is a yellow flag.** The gate confirmed *zero* Highs across 46 mechanisms. We cannot tell from
   this corpus whether that is correct (zetachain's contract layer genuinely has no permissionless-material theft —
   plausible) or whether the reject-first bar is **too aggressive**. P201 validated the gate's **negative** behavior
   (correctly demoting non-Highs) but **not** its **positive** behavior (confirming a true permissionless contract-High).
3. **Oracle (B) and precision (C) under-tested.** Oracle: N/A (carved out, UNVALIDATED_OUT_OF_SAMPLE). Precision:
   only lightly present (gas-fee/accounting), graded Medium/Harness — directional only.

## Net vs P200
P200 (predy): refined-less gate fixed 1/4 over-HIGH; oracle/precision over-rated; H-02 folded. P201 (zetachain):
refined gate fixed **6/6** matched over-HIGH; per-mechanism grading removed folding; **but** could not test
High-preservation (corpus Highs off-chain). The refinement clearly improved the **demotion** axis; the
**preservation** axis still lacks a corpus to validate it.
