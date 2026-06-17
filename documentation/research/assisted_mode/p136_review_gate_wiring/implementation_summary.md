# P136 — Implementation Summary

Wires the P135 advisory surfacing into the pipeline review-gate so existing mechanism-detector hits reach
`review_gate.md` automatically as **advisory_only** context. No new detector; no detection/severity/submission/
gate logic change.

## Files changed
1. **`run_pipeline.sh`** (3 additive lines, all non-blocking):
   - `coverage_review_gate()` battery: added `units_invariant_audit.py … || true` (report-only; provides the
     units H-01 advisory input). research-only detectors (semantic_tvl/registry) were **not** added — they stay
     research-only.
   - `full` and `review-gate`: added `surface_mechanism_advisories.py 2>/dev/null || true` immediately before
     `generate_review_gate.py`. Never blocks the coverage/min-confirm/bridge gates or the pause.
2. **`scripts/generate_review_gate.py`**: new `_advisory_section()` reads `output/mechanism_advisory_context.json`
   and appends a clearly-separated **"## Advisory Context — NOT confirmed (mechanism detectors)"** section
   (bold disclaimer that all rows are `advisory_only=true` / `submission_ready=false` / `requires_human_review=
   true`; a detector/status/location/mechanism/confidence/route-reason table; a Deep-pass recommendations
   subsection). Inserted after Finding Details, before the file write. **Advisories are never added to
   `findings`** → the confirmed-findings count and the Validated Findings table are unchanged. Robust by
   contract: missing / malformed / disabled (`surfaced:false`) / empty context → returns `[]` (no section, no
   error).
3. **`tests/mechanism_advisory/test_review_gate_advisory_section.py`** (new, 8 tests).

## No config change
Reuses the existing `mechanism_advisory.surface_mechanism_advisories` master flag — off → surfacing writes a
disabled stub → review_gate renders no section (verified). Production default: advisory+report surfaced,
research-only off, standalone queue off.

## Behavior (noya, production default, via the wired flow)
`review_gate.md` gains the advisory section with 26 advisories (CPA 7, AC 9, units 10), the 3 P133 MISS, and 10
deep-pass recommendations incl. `NoyaValueOracle._getValue → deep_pass_value_provenance`; confirmed-findings
count 0 (unaffected); advisories absent from Validated Findings. Master gate off → no section.
