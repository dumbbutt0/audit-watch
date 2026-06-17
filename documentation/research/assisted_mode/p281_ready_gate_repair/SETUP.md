# P281 — SETUP (READY gate repair; REPAIR phase)

Make the auto-derived READY_FOR_POC_INTENT label HARDER to earn by reading the actual function BODY (source span), not
just manifest metadata. Repairs D1 inline-guard / D2 state-machine / D3 value-flow / D4 source-span. Research-only;
advisory; no production authority; no candidate becomes reportable/confirmed/severity. Mindset: don't widen discovery
until READY is trustworthy.

## Allowed edits (this phase)
- scripts/research/completion_evidence_deriver.py + poc_readiness_evidence_gate.py (the gate/deriver).
- NEW scripts/research/source_span_guard_extractor.py (sha `9a4028b807dc4e7a`) + config/research_poc_readiness_gate.json.
- NEW tests/research/test_p281_ready_gate_repair.py; this doc dir; pocs/p281/.

## Back-compat: D1-D4 activate ONLY when a real function body is resolvable (manifest item file+source_span). Synthetic
inputs (no readable file) -> gate_evidence.body_available=False -> pre-P281 (P279) path. P279/P280 tests stay green
(24/24 verified). No test pins the deriver/gate by hash.

## Byte-identical (verified): P260/P262/P264/P267/P269/P271/P273 router code 6debb753+config 91f9deac/P277/P278 glue +
forbidden 5. Active audit symlink -> audits/size-credit-2024-06-blind/output. No contest/production source edits.
