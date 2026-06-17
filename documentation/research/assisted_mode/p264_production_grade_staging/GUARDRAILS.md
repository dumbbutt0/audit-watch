# P264 — GUARDRAILS (runtime, fail-closed)
_enforce_guards() asserts NO advisory candidate sets: severity (non-null) · reportable=true · submission_ready=true ·
concluded=true · emits_finding=true · production_routing=true · status!=ADVISORY_RECALL_CANDIDATE.
On ANY violation: write recall_guard_report.json (result FAIL + per-violation detail), exit nonzero (2), emit NO
advisory outputs (fail closed — no partial promoted output). Config validation: caps must be positive ints within
cap_hard_upper_bounds, else fail closed. Missing/unreadable inputs → fail closed. Verified: malformed config → exit2
no output; missing input → exit2 no output; clean shadow run → guard PASS 0 violations.
