# P130 — Holdout Sanity Check

Goal: confirm the repair is **not Beanstalk-only** and **not blanket inflation**. Beanstalk source is absent
on disk, so the repair was *developed and measured on two other audits* — making this entire phase a holdout
test by construction (the repair never saw Beanstalk source).

## noya-2024-04-eval (library/strategy-heavy — should benefit)
- candidate count: 1649 items (unchanged); high-surface in-scope fns **158 → 228**; 70 boosted.
- recovered correct-contract leads: **awarded-FUNCTION coverage 32% → 74%** (+8 functions, mostly internal
  `_getPositionTVL`/`_getValue` value-logic). awarded-CONTRACT 89% → 95%.
- new suspicious noise: +70 deep-pass-eligible functions, all risk-tagged helper logic (capped at 3/contract).
- broken paths: none. test failures: none.

## decent-2024-01-holdout (bridge, no libraries — should be ~unchanged)
- candidate count: 100 items (unchanged); high-surface **46 → 52**; 6 boosted.
- recovered correct-contract leads: **awarded coverage unchanged (33%)** — its uncovered awarded functions
  are `(absent)` (in `lib/decent-bridge/src`, outside the `--contract src` root), a root artifact, not a
  scoring miss. The repair correctly does **not** manufacture coverage where there are no risk-tagged helpers.
- new suspicious noise: +6 (view functions carrying oracle/token tags) — modest, targeted.
- broken paths: none. test failures: none.

## Interpretation
- The repair fires **proportional to architecture**: large effect on a library/internal-heavy audit (noya),
  small effect on a non-library audit (decent). This is the signature of a *general* source-resolution fix,
  not an overfit: it helped a **non-motivating** audit's awarded-function coverage by +42 pp, and it cannot
  have been tuned to Beanstalk (Beanstalk source was unavailable throughout).
- One residual class the ranking repair does **not** address: a genuinely **absent** function
  (`SNXConnector._getPositionTVL`) — an enumeration/scope-membership gap, correctly out of scope for a
  ranking fix (flagged for a follow-on).
