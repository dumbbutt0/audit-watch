# P208 — recommendation

## Decision: `L3_POLICY_DRY_RUN_READY`

The validated L3 realized-impact HIGH standard is now operationalized as a **dry-run severity policy** — advisory
only, un-wired, with production byte-identical START==END.

## What ships
- **`L3_HIGH_POLICY.md`** — threat-ceiling-vs-final-severity, L1/L2/L3 tiers, the `high_promotion_allowed` rule,
  demotion/NEEDS_HARNESS mapping, human-override requirements, non-submission guarantee.
- **`L3_READINESS_SCHEMA.json`** — draft-07 evidence contract (aligned with `severity_calibration.schema.json`).
- **`scripts/validate_p208_l3_readiness.py`** — un-wired `validate`/`decide`/`backtest` helper; computes
  `high_promotion_allowed` + blocker + `calibrated_severity` + submission_state; submits/routes nothing.
- Backtest + regression fixtures, scorecard, regression checks, submission-readiness linkage, integration notes.

## Results (all advisory; `python scripts/validate_p208_l3_readiness.py backtest`)
- **Backtest 4/4:** decent H-01 & vultisig H-01 (executed L3 PoC + control + permissionless + prod-unmodified) →
  `high_promotion_allowed=true`; decent M-03 & vultisig M-03 (no material value movement) → blocked, calibrated Medium.
- **Regression 6/6 blocked:** static-High-no-PoC, DoS/griefing, precision-no-magnitude, source-refuted, decent-06
  false-High, decent-12 NEEDS_HARNESS.
- **10/10 expected matches, 0 false-allows, 0 false-blocks, schema 10/10 pass, 0 dashboard mismatches.**

## Why this is safe
- No production prompt/checker/router/ledger/detector/dashboard change; no wiring; no auto-submit; no
  promotion/demotion of real findings; no canonical-label/answer-key change.
- Mirrors the existing research-only `submission_readiness_review.py` invariants; every artifact carries
  `research_only:true`/`routes_in_production:false`; human review remains mandatory for any HIGH package.

## Campaign status
The severity-calibration frontier (open since P186) is now closed end-to-end: **measured** (P199) → **principle**
(P204 L3 executed standard) → **generalized** on 2 corpora (P207) → **operationalized as a dry-run policy** that, on
the validated controls + regressions, preserves genuine L3 Highs and blocks capability-only/over-rated Highs with 0
false-allows / 0 false-blocks.

## Next (NOT this phase; human decision)
Whether/how to **wire** the L3 gate into the real submission-confirm path — relative to the existing
`min_confirm_gate`/`confirm_gate` — plus a cost model for L2/L3 harness authoring (auto-scaffold vs human). Optional:
surface the `decide()` panel read-only in `scripts/dashboard.py`. Deep-pass recall + oracle track remain separate. Do
NOT wire until that design is reviewed.
