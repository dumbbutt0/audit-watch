# P135 — Implementation Summary

## Files (additive only)
1. **`scripts/surface_mechanism_advisories.py`** (new) — reads the 5 detector `output/*_audit.json`, normalizes
   to advisory entries, dedups, attaches to candidates, applies status-gates + caps, writes
   `output/mechanism_advisory_context.json`, optionally appends review_context to `human_review_queue.jsonl`,
   and emits H-03-class `deep_pass_value_provenance` recommendations. Pure functions (`normalize_hits`,
   `dedup`, `apply_status_gate`, `apply_caps`, `attach_candidates`, `recommend_deep_pass`, `build`) + an I/O
   `main()`. Never mutates detectors/severity/submission.
2. **`config/agent_policy.json`** (+`mechanism_advisory` block): `surface_mechanism_advisories`,
   `surface_research_only_advisories`, `mechanism_advisory_standalone_queue`, `mechanism_advisory_max_per_detector`,
   `mechanism_advisory_max_total`, `mechanism_advisory_allowed_detectors`. Script has safe defaults so it runs
   without config.
3. **`tests/mechanism_advisory/test_surface_mechanism_advisories.py`** (new, 13 tests).

## Key design choices
- **Mirrors `advisory_escalation_gate`** ("never converts advisory to finding") but targets the *standard*
  review surface (a separate artifact + gated queue), not the strict-full-audit escalation path.
- **Detector-status preserved verbatim**; research-only surfaced only when `surface_research_only_advisories`
  (and queued only if that AND standalone-queue). report-only (units) surfaced at production default.
- **Confidence-prioritized caps:** caps sort by confidence (high>med>low) before truncating, so a blunt cap
  never drops a high-signal hit — this is what keeps units_invariant's 10 high-risk entries (incl. the H-01
  Chainlink decimals MISS) when 45 hits are capped to 10. General signal-priority, not target-specific.
- **Deep-pass recommendations ordered oracle-tag-first** so the cap keeps the strongest value-provenance loops
  (recovers the H-03 NoyaValueOracle._getValue class generally — no contract names).
- **`--eval`** widens to research-only + standalone queue; production default keeps research-only off and queue
  off (capped).

## Behavior (noya, production default)
26 advisories (CPA 7, AC 9, units 10), 0 research-only, 10 deep-pass recs, 0 queued. `--eval`: 39 advisories
(+STC 10, RPL 3 research-only), 39 queued. Master gate off → 0 advisories (fully reversible).
