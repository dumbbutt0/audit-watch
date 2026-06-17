# P142 — Problem Statement

P139→P141 built and validated an advisory-only value-provenance completion loop (P139 queue → P140 `ingest_results`
→ P141 cross-architecture measurement). **P141's measurement was manual and throwaway**: queues were hand-authored
with `queue_origin:eval_only_manual_queue`, real P137/P138 blind outputs were ingested, and the temp artifacts were
deleted afterward. There was no standing, repeatable instrument.

**P142 turns that into a standing instrument** — a reusable, config-gated, **research-only, UN-WIRED** harness that:
1. **seeds** eval-only value-provenance queues from a corpus registry,
2. **ingests** already-recorded REAL blind/manual deep-pass outcomes through the *unchanged* P140 safety merge,
3. emits a **cross-architecture conversion scorecard** with a **time-series**,
so finding/strong_clear/needs_human conversion and the clean-false-finding rate can be tracked over time and used
as a **regression baseline**.

## Invariant (research-platform Layer pattern)
**"Aggregate, don't adjudicate."** The harness refuses the next layer's job: it never routes, confirms, sets
severity/exploitability/submission, touches an audit's production `output/`/`review_gate.md`, or wires into
`run_pipeline.sh`/`agent_policy.json`. Every output carries the four research flags (`is_gate:false`,
`research_only:true`, `routes_in_production:false`, `routed_manifest_ids:[]`) + `routing_allowed:false`; routed
inputs are refused; provenance-less corpus rows are refused (no fabrication).

## Outcome
The harness reproduces the **P138 full-corpus baseline** exactly from real recorded outcomes: 11 items, 11
completed, finding 3 / needs_human 1 / strong_clear 7, **useful_recall 0.80**, strict_recall 0.60,
**clean_false_finding_rate 0.0** — and contains the P141 7-job subset within it. No production file was touched.
