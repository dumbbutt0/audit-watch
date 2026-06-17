# P273 — SETUP (Award-Class Coverage Layer)

**RESEARCH-ONLY · DEFAULT-OFF · ADVISORY · NARROW.** Adds one new thing — an award-class coverage router — between
the P267 selector and the P269 impact-first triage, so a single award class can't monopolize PoC slots. Touches
nothing else.

## The P272 bug being fixed
P272 (blind, init-capital) proved the family→exact bridge generalizes (exact real-code recovery of the Init
`LiqIncentiveCalculator` cap-ordering bug pre-reveal), but **0 awarded recovery**: Init's 7 awards were entirely in
**MarginTradingHook order-validation / access-control / front-running / DoS**, while impact-first triage over-weighted
the **lending-accounting** class. Objective mismatch: *valid exact bug ≠ awarded bug.*

## Goal (precise)
**NOT "prefer access control."** It is **"don't let any one award class monopolize triage."** Before final PoC
routing, represent the top plausible award classes; P269 still ranks by impact INSIDE each represented class.

## What P273 adds (allow-list only)
- `scripts/research/award_class_coverage_router.py` — deterministic 11-class coverage router.
- `config/research_award_class_coverage_router.json` — class signal keywords, budget, advisory contract.
- `tests/research/test_p273_award_class_coverage_router.py`.
- `documentation/research/assisted_mode/p273_award_class_coverage/` (8 docs + outputs).

## Pipeline position (does NOT replace P269)
`advisory → P267 selector → P273 coverage router → P269 impact-first triage per represented class → completion → PoC`.

## Design stance (honest)
Deterministic classification over **source-derivable signal keywords** per candidate (locus/function/templates/
signal text), NOT award labels. Backtest uses award labels ONLY to score whether the awarded class was routed; labels
never enter the router. No answer key, no source-reading LLM, no network.

## Frozen baselines (verified unchanged; must stay byte-identical)
P260 `d6b494bc` · P262 `a48336275f` · P264 `85f9cbe6` · P267 `b0623b8c` · P269 `63c88d02` (+ configs) · P271 checklist.
Forbidden 5: dashboard_sync `c1af70e1` · deep_trace `c095c426` · min_confirm_gate `2a15169a` · confirm_gate `afc481c9`
· validate_p208 `ae55eb80`. Active audit `output → audits/size-credit-2024-06-blind/output`.

## Backtest inputs (frozen scored reveals — no new answer keys)
P272 (Init) · P270 (Wise) · P268 (Karak) · P266 (Phi) · P263 (BendDAO) REVEAL_AND_SCORE docs.
