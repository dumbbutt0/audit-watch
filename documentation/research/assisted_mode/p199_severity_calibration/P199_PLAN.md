# P199 — plan (frozen)

Read-only cross-corpus severity-calibration study: measure whether the over-HIGH skew (P198 FM-1, P186/P187
frontier) is systematic before proposing any fix.

Sequence (executed): 1 integrity precheck (START hashes) → 2 dataset construction (validate_p199.py over
P186/P189/P198 raw_outputs + scoring tables + answer-key-id severities) → 3 measure calibration (over-HIGH on
Medium/Low-awarded subset; controlled all-Medium corpus skew; confound exclusion of High-awarded) → 4 failure
taxonomy → 5 High-vs-Medium discriminators → 6 severity-gate proposal (DESIGN NOTE ONLY) → 7 decision.

Guardrails: read-only; no production prompt/checker/router/detector/severity/route edits; no deep_trace.md patch;
gate is a design note only; verdict treated as a threat ceiling (not calibrated severity); integrity recorded
start & end; fabrication_rate=0.

Decision space: SEVERITY_FRONTIER_CONFIRMED · NO_SYSTEMATIC_SEVERITY_SKEW · DATASET_TOO_THIN ·
MIXED_CAUSES_NEED_MORE_CORPORA · INVALID_RUN. **Outcome: SEVERITY_FRONTIER_CONFIRMED** (see P199_RECOMMENDATION.md).
