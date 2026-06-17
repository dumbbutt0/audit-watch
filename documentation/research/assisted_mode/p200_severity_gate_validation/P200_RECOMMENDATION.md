# P200 — recommendation

## Final decision: `SEVERITY_GATE_PARTIAL` — do NOT ship the P199 gate

The P199 severity-gate discriminator was validated **out-of-sample** on a fresh sealed corpus (predy-2024-05,
4 High / 8 Medium), with a double freeze (blind verdicts, then offline calibration, both before the seal opened).
It **partially** holds — and the part that fails is the part that matters.

### What held ✓
- **Threat-ceiling skew reproduced:** 14/16 (87.5%) of blind surfaces ceil at HIGH on an 8/12-Medium corpus —
  the P199 structural finding (verdict = threat ceiling, not severity) generalizes cleanly.
- **Griefing/DoS → Medium generalizes:** predy-06's recipient-revert liquidation-brick (awarded M-06) was
  correctly demoted HIGH→Medium; predy-11 (M-01) and predy-15 correctly kept Medium. The reject-first DoS rule works.
- **No clean false-demotion:** no separately-found awarded High was demoted to Medium/None.

### What failed ✗ (the decisive part)
- **Over-HIGH reduction is weak: 4/5 → 3/5 (one fixed).** On the mechanism-matched awarded-Medium subset, the gate
  removed only **1 of 4** over-HIGH cases. P199's in-sample 8/8→0/8 did **not** hold out-of-sample.
- **The 3 unfixed are ALL oracle/precision:** Chainlink staleness (M-04, predy-07/09) and negative-tick rounding
  (M-03, predy-10) were rated **Medium** by predy's judges but the gate kept them **High** — applying P199's
  *oracle-manipulation→insolvency=High* rule (from in-sample revert-lend). **Oracle/precision severity is
  corpus-context-dependent and the rule over-rates it here.**
- **Surface-level grading buried a genuine High:** the one awarded-High found by mechanism (H-02) was a *secondary*
  mechanism on a Medium-primary surface, so the surface-level label under-graded it. A production gate must grade
  **per mechanism**, not per surface.

## Why this is the right call (and vindicates the burden-of-proof discipline)
P199 explicitly flagged the fit-on-same-data caveat and made this blind out-of-sample run the precondition to any
`deep_trace.md`/checker change. The run paid off: it caught that the discriminator does **not** generalize on
oracle/precision severity. Shipping on the in-sample 8/8 would have introduced a mis-calibrated production gate.
This mirrors P195/P196 (read-only validation prevented shipping a 0-gain change).

## Recommended next (each needs explicit go — NOT actioned here)
1. **Do not wire the P199 gate.** It is not validated out-of-sample.
2. **Refine the discriminator before any re-test:** (a) make oracle-staleness / price-precision / TWAP severity
   *evidence-conditional* (proven drain magnitude → High; bounded mispricing / liveness → Medium) instead of a
   blanket oracle→High; (b) grade **per carried mechanism**, not per surface (fixes the H-02 folding); (c) keep the
   griefing/DoS→Medium rule (it generalized).
3. **Re-validate on a second fresh corpus** with more *mechanism-matched* findings before reconsidering (predy gave
   only n=5 matched Mediums + 1 matched High — directional, not definitive).
4. The recall misses on H-01/H-03/H-04 (wrong mechanism on reallocate/liquidation surfaces) are a **deep-pass
   recall** matter (P183–P188 frontier), separate from the severity gate.

## Decision-space justification
- Not `SEVERITY_GATE_VALIDATED_OUT_OF_SAMPLE`: over-HIGH did **not** drop materially (1/4 fixed) and oracle/precision
  over-HIGH persists.
- Not `SEVERITY_GATE_FAILED_FALSE_DEMOTIONS`: no clean awarded-High was demoted to Medium/None (the H-02 issue is a
  surface-vs-mechanism methodology gap, not a rule false-demotion).
- Not `DATASET_TOO_THIN`: predy has real H+M; the thin part (n=5 matched) is recorded as a power caveat, not a
  reason to discard the clear oracle/precision signal.
- `SEVERITY_GATE_PARTIAL` fits: real partial generalization (DoS rule yes; oracle/precision no).

## Acceptance criteria — met
Fresh corpus ✓ · answer-key access controlled (count-only viability; full only after both freezes) ✓ · double
freeze recorded (`4aede343` / `1e158f1e`) ✓ · gate applied offline/read-only only, **not** implemented in
production ✓ · original ceiling and calibrated severity scored **separately** ✓ · over-HIGH change measured ✓ ·
genuine-High preservation measured ✓ · blind firewall (prompts + outputs leak-scan CLEAN, scorer post-freeze) ✓ ·
`fabrication_rate=0` ✓ · production hashes byte-identical START==END ✓ · JSON valid ✓.
