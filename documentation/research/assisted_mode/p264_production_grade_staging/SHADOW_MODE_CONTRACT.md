# P264 — SHADOW_MODE_CONTRACT
Shadow mode emits exactly 4 files in --out-dir: recall_advisory_candidates.json · recall_advisory_candidates.md ·
recall_metrics.json · recall_guard_report.json.
Every advisory candidate MUST carry: candidate_id, locus, contract, function, source_span, prioritizer_score,
sweep_inclusion_reason, templates_applied, generated_mechanisms, bc_ranking_handoff, completion_status,
refutation_status, evidence_pointers, status="ADVISORY_RECALL_CANDIDATE", promotion_label, severity=null,
reportable=false, submission_ready=false, concluded=false, emits_finding=false, production_routing=false.
Promotion label ∈ {NEEDS_RANKING, NEEDS_COMPLETION, NEEDS_REFUTATION, READY_FOR_HUMAN_REVIEW_SHADOW}. NEVER
{confirmed, reportable, submission_ready, severity High/Medium/Low}. The harness participates in NO production
routing, NO confirmation gates, NO dashboard confirmed-state. Increase recall WITHOUT letting raw candidates become
findings: promotion requires the SEPARATE downstream ranking/completion/refutation + human review.
