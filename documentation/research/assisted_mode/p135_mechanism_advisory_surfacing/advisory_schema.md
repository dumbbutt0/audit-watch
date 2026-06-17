# P135 — Advisory Evidence Schema

Written to `output/mechanism_advisory_context.json` (`routing_allowed:false`, `submission_ready:false`,
`research_only_summary:true`). Each `advisories[]` entry:

| Field | Meaning |
|---|---|
| `source_detector` | connector_position_accounting / arithmetic_conservation / units_invariant / semantic_tvl_completeness / registry_position_lifecycle / deep_pass_router |
| `detector_status` | production / advisory / report_only / research_only (preserved verbatim) |
| `advisory_only` | **always true** |
| `submission_ready` | **always false** |
| `requires_human_review` | **always true** |
| `audit_id`, `contract`, `function`, `file_path`, `line` | location |
| `mechanism_class` | the detector's shape/category (verbatim) |
| `evidence_summary` | the detector's reason/signals (truncated; no new claim) |
| `confidence` | low/medium/high — **copied verbatim, never relabeled** |
| `route_reason` | why it's surfaced + suggested specialist |
| `suggested_specialist` | logic / arithmetic (advisory only) |
| `related_candidate_id` | set if it matches a merged_findings candidate (else null) |
| `related_review_queue_id` | optional link |
| `source_output_path` | the detector JSON it came from |
| `allowed_next_steps` | inspect_source · run_deep_pass_value_provenance · map_defenses · build_poc_if_confirmed · reject_if_design_intended |
| `forbidden_next_steps` | submit_directly · assign_severity_without_impact · mark_confirmed_without_poc_or_human_review |

**No `severity`, `status:confirmed`, or submission field is ever emitted.**

## Deep-pass recommendations (`deep_pass_recommendations[]`)
review_context-only entries for the H-03 class (oracle/value/accounting-tagged function with a loop + loop-
carried call): `recommended_prompt: deep_pass_value_provenance`, `prompt_reason`, `mechanism_class:
value_provenance_loop`, `advisory_only:true`, `submission_ready:false`. **Not a finding; no severity.** Ordered
oracle-tag-first so the cap keeps the strongest value-provenance loops.

## Standalone queue entry (gated)
`{advisory_id: "ADV-<DET>-NNN", review_context:true, advisory_only:true, submission_ready:false,
requires_human_review:true, finding_id:null, recommended_severity:null, source_detector, detector_status,
contract, function, file, mechanism_class, evidence_summary, related_candidate_id, queued_at}`.
