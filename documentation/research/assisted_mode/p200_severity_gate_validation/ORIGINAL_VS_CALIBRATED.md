# P200 — original threat-ceiling vs calibrated severity

Scored **separately**, as required. "Original" = blind `deep_trace.md` verdict (threat ceiling). "Calibrated" =
offline P199 gate label, frozen before the seal opened.

## Headline
| metric | original (ceiling) | calibrated (gate) |
|---|---|---|
| surfaces ≥ HIGH | **14 / 16 (87.5%)** | **6 / 16 (37.5%)** |
| over-HIGH on matched awarded-Medium | **4 / 5** | **3 / 5** |
| of which fixed by the gate | — | **1** (predy-06, griefing/DoS) |
| still over-HIGH (all oracle/precision) | — | **3** (predy-07/09 = M-04, predy-10 = M-03) |
| genuine-High mechanism found (H-02) preserved at High | n/a | **0 at surface level** (folded under Medium) |
| clean false-demotion of a found High to Medium/None | — | **0** |

## Reading
- The blind ceiling **reproduces the P199 over-HIGH skew out-of-sample**: 87.5% of examined surfaces ceil at HIGH,
  on a corpus that is 8/12 Medium. Confirms the "verdict is a threat ceiling, not a severity" structural fact again.
- The gate **does cut the gross HIGH count** (14→6), but most of that cut lands on **unawarded** surfaces (recall
  FPs routed to Harness) — not on the awarded-Medium surfaces that actually needed demoting.
- On the surfaces that matter (mechanism-matched awarded-Medium), the gate fixed **only 1 of 4** over-HIGH cases.
  The 3 it failed are **all oracle/precision** (Chainlink staleness, negative-tick rounding) — categories the
  P199 discriminator treats as genuine-High (per the in-sample revert-lend oracle precedent), but which **predy's
  judges rated Medium**. The discriminator's oracle/precision severity rule does **not generalize** to this corpus.
- The one genuine-High the blind run found (H-02) was **carried as a secondary mechanism** on a surface whose
  *primary* was the Medium M-06, so the surface-level grade (Medium) **under-represents H-02**. A per-mechanism gate
  would grade H-02 High; the surface-level application used here does not.

## Contrast with P199 (in-sample)
P199 on its own dataset: over-HIGH **8/8 → 0/8**, 0 genuine-High demotions. P200 out-of-sample: over-HIGH
**4/5 → 3/5**. The in-sample result did **not** hold out-of-sample — the fit-on-same-data caveat P199 flagged is
now measured, and it is the decisive reason not to ship.
