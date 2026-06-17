# P273 — IMPLEMENTATION_NOTES

`scripts/research/award_class_coverage_router.py` + `config/research_award_class_coverage_router.json`. Deterministic;
no answer key; no source-reading; no network; un-wired; does not import/modify P260/P262/P264/P267/P269/P271.

## Classification (signal keywords, not award labels)
Each candidate's text = locus + function + contract + `signals` + `templates`, lowercased. The class = the one with
the most matched keywords from `class_signals` (tie-break by `class_order`). 11 classes incl. UNKNOWN_OTHER. The
backtest's award labels are NOT in the input (used only to score outcomes).

## Plausibility (anti-drama gate)
`plausible` iff `impact_supported != false` AND `selector_outcome != REFUTE_*_FIRST` AND no infeasible blocker AND
(`recall_delta` OR `signal_strength >= min_signal`). A properly-gated admin function with only a stray `onlyOwner`
keyword and no recall-delta / weak signal is NOT a routed representative.

## Coverage selection (anti-monoculture core)
- Group plausible candidates by class; best-first within class (signal+recall-delta+order).
- Rank classes by best-candidate score; cap at `max_classes`.
- **Round 1:** route ≥1 representative per distinct plausible class (round-robin) up to `poc_budget`.
- **Round 2:** fill remaining slots with 2nd reps of the strongest classes — but ONLY after every plausible
  `monoculture_guard_class` (ACCESS_CONTROL / ORDER_VALIDATION / FRONT_RUNNING_MEV / DOS_LIVENESS) has ≥1 rep. This is
  the hard anti-monoculture rule: accounting (or any class) cannot take a 2nd slot while a guard class has 0.
- Heavy/harness-weight candidates → `COVERAGE_SELECT_HEAVY` (still routed — the P269 lesson).

## Labels
SELECT / SELECT_HEAVY (routed) · CONTROL (plausible, class not yet repped but budget spent) · DEFER_LOW_SIGNAL ·
DEFER_DUPLICATE_CLASS (class already repped) · DEFER_INFEASIBLE · UNKNOWN.

## Advisory contract + guard
Every decision hard-stamps `severity:null` + 6 false promotion flags + `status:ADVISORY_COVERAGE_DECISION`. Runtime
guard writes FAIL `coverage_guard_report.json` and exits 2 (no output) on any leakage / unknown label. Config
validation fails closed on unsafe flags, non-positive caps, or caps above hard maxima. Malformed/missing input → exit 2.

## Output
`{selected_classes, representatives_per_class, class_rationale, skipped_classes, handoff_queue_to_p269, decisions}` +
markdown. `handoff_queue_to_p269` = the SELECT_* ids → fed to P269 impact-first triage (which ranks by impact WITHIN
each represented class). The router does NOT replace P269; it guarantees cross-class representation upstream of it.
