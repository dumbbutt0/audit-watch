# P135 — Problem Statement

P134 found **ROUTING_GAP_NOT_DETECTOR_GAP**: existing mechanism detectors recover 7/8 of the P133 noya targets
(all 3 P133 MISS) but their output doesn't reach review — units_invariant is report-only, semantic_tvl/
registry_position_lifecycle are research-only, connector_position_accounting/arithmetic_conservation escalate
only in strict-full-audit. So the surface specialist misses what the mechanism layer already detects.

**Primary question:** Can the pipeline surface existing mechanism-detector hits into human review so the P133
MISS/PARTIAL cases reach review, **without creating unsafe promotions**?

**Approach:** a routing/surfacing layer (`scripts/surface_mechanism_advisories.py`) that reads existing detector
outputs and emits **advisory review_context** — every entry `advisory_only:true`, `submission_ready:false`,
`requires_human_review:true`. No new detector, no detection/severity/submission logic change. research_only /
report_only status preserved; config-gated and capped; master switch disables all.

**Success bar (strict):** P133 MISS/PARTIAL reach review AND nothing becomes submission-ready or confirmed.
