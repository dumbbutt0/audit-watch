# P278 — BUDGET_AND_QUEUE_POLICY

Three DISTINCT budgets (a candidate advancing one does NOT gain reportability):
- **handoff budget = 10** (router `poc_budget`): candidates allowed into deeper validation.
- **validation-queue budget = 10** (`expanded_validation_queue`): candidates that must gather an evidence package +
  complete mechanism reasoning (coverage-balanced from the handoff).
- **PoC execution budget = 5** (`poc_readiness_evidence_gate`): at most 5 READY candidates flagged for runtime; extra
  READY -> DEFER_POC_BUDGET. Reportability stays forbidden without strict-gate evidence regardless of any budget.

## Validation-queue composition (when candidates exist)
class minimums (accounting≥2, access≥1, order≥1, front-run≥1, DoS≥1, math/share≥1, oracle≥1, external≥1) +
≥1 recall-delta + ≥1 high-impact heavy-runtime + ≤1 pure control. **Anti-monoculture:** no class > 40% of the queue
unless <3 plausible classes. **Anti-easy-PoC** + **anti-drama** inherited from the frozen selector/router plausibility
(impact_supported + falsifiable mechanism; a severe-sounding label alone never routes).

## Operator-burden control
Validation queue capped at 10/contest; corpus avg 7.0. PoC budget caps runtime work at 5/contest. The readiness gate
keeps the operator from spending runtime on incomplete-evidence candidates (they sit at NEEDS_MORE_EVIDENCE).
