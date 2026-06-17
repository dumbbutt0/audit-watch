# P209 — current confirm/submission path (mapped from real code, read-only)

## Flow (text diagram)
```
discovery / specialists (Step 2)            <- candidate creation; severity = deep-trace THREAT CEILING
        |
        v
synthesis -> merge -> ICE -> multi-pass -> FP check -> pre-submission gate -> dupe screen   (Steps 2.5..3.8)
        |
        v
triage (Step 4)  -> data/triage/{submit,poc_required,defer,reject}.jsonl   (recommended_severity assigned here)
        |
        v
[A] min_confirm_gate.py        (FIELD PRESENCE; GATED_BUCKETS = submit, poc_required)
        |   requires: entrypoint, manifest_refs, preconditions, impact, guards+why,
        |             smallest-PoC/repro plan, severity_ceiling, confidence, not-dup reason
        |   writes output/min_confirm_gate.json ; block => exit 1 (override AUDITWATCH_MINCONFIRM_OVERRIDE=1)
        v
[B] confirm_gate.py --mode submission [--strict]   (REACHABILITY TRUTH)
        |   reads output/confirm/reachability_analysis.json
        |   FAIL_STATUSES = {external_entrypoint_missing, privileged_only, dead_path, insufficient_evidence}
        |   submission mode: HARD-FAIL High/Critical that are non-credible; --strict adds Medium + 'uncertain'
        |   writes output/confirm/confirm_gate.json ; (override AUDITWATCH_CONFIRM_OVERRIDE=1)
        |   [run_pipeline.sh submission-confirm = A then B]
        v
[C] submission_readiness_review.py   (HUMAN readiness OVERLAY, research-only, append-only)
        |   READINESS_STATES incl. blocked_by_missing_poc / blocked_by_missing_impact /
        |             blocked_by_severity_too_low / ready_for_submission_package / needs_more_context
        |   writes output_research/human_submission_review/submission_readiness.jsonl
        |   NEVER flips canonical submission_ready / routing_allowed ; gated by finding facts + checklist
        v
[D] final_submission_pack.py   reads data/triage/{submit,poc_required}.jsonl + output/merged_findings.json
        |   -> output/submission_pack.{md,json}   (human submits manually)
        v
[E] dashboard.py / findings_overview.py / finding_detail.py  (DISPLAY only)
            dashboard computes a display submission_ready (~L398); detail/overview stamp
            submission_ready:false / routing_allowed:false / research_only:true
```

## Where key things happen
- **Severity assigned:** deep-trace emits a THREAT CEILING (CRITICAL/HIGH/MEDIUM_THREAD) at discovery; triage sets
  `recommended_severity`; `min_confirm_gate` requires a `severity_ceiling` field but does not *prove* magnitude.
- **`submission_ready` / `routing_allowed`:** never set true by any gate in the research-only config; they are
  display-only (`dashboard.py`) or stamped false (`finding_detail.py`/`findings_overview.py`). `api_free=true`.
- **Real blocking gates:** `min_confirm_gate` (field presence) and `confirm_gate` (reachability credibility). Both are
  deterministic, no-LLM, override-able by env.

## The gap L3 fills
Neither gate proves **realized impact magnitude**. `confirm_gate` proves an entrypoint is attacker-credible/reachable;
it does NOT prove the High actually moves material value. That is precisely the L3 realized-impact standard (P204/P207):
an executed PoC showing material theft/loss/insolvency/privileged-control. So L3 is **additive**, sitting after
reachability confirmation, before a candidate is treated as High-submission-ready.
