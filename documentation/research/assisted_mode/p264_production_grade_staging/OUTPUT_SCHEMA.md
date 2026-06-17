# P264 — OUTPUT_SCHEMA
Shadow advisory output is validated by schemas/recall_first_advisory.schema.json (draft-07; NEW additive shadow-only
schema — NOT a canonical finding schema, not referenced by production). It pins: module=recall_first_harness,
is_gate=false, research_only=true, routes_in_production=false, emits_findings=false, concludes_vulnerability=false,
guard_violations=0, and per-candidate severity=null + reportable/submission_ready/concluded/emits_finding/
production_routing=false + status=ADVISORY_RECALL_CANDIDATE + promotion_label∈enum. Verified: benddao + hybra shadow
outputs validate against the schema (jsonschema 4.26.0).
