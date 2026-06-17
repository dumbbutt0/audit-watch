# P264 — TEST_RESULTS
- disabled mode → no-op, emits nothing, exit 0. ✓
- shadow mode (benddao, hybra) → 4 files; guard PASS (0 violations); 17 advisory candidates; 30 mechs; all flags
  clean (severity null; reportable/submission/concluded/emits_finding/production_routing false). ✓
- schema validation (jsonschema 4.26.0): benddao + hybra outputs VALID. ✓
- fail-closed: malformed config (negative cap) → exit 2, no advisory output. ✓ ; missing input → exit 2, no output. ✓
- metrics record P260/P262 module hashes + reproducibility (git=n/a, command, input hashes). ✓
- caps enforced (≤25 loci, ≤5 mech/locus). ✓
- reused P260/P262 modules byte-identical; forbidden files byte-identical; active audit unchanged. ✓
- backward-compat: P260/P262/P263 + checkpoint guard tests still green. ✓
See test_p264_production_grade_staging.py.
