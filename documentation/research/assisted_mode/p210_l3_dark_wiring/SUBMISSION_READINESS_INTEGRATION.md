# P210 — submission_readiness_review.py integration

Hash `b435a635` → `7c4b563d`. All additions guarded by `_l3_enabled()`.

## Additions
- `import os`; `_l3_enabled()`; `L3_DIR = output_research/l3_readiness/`; `_L3_HIGH_TARGETS={"High","Critical"}`.
- `READINESS_STATES += {"blocked_by_missing_l3_poc"}`; `DISPLAY_SUBMISSION_STATUS["blocked_by_missing_l3_poc"]="BLOCKED_L3"`
  (and the pre-existing `display_submission_status` already maps any `blocked_by_*` → "BLOCKED").
- `_load_l3_record(candidate_id)` — reads `L3_DIR/<id>.json`; missing/malformed → `None` (fail-closed handled in eval).
- `l3_evaluate(record, severity_target)` — PURE; non-High target → `{"applies": False}`; High/Critical → runs imported
  P208 `decide(record or {})` and returns advisory fields (`high_promotion_allowed`, `high_promotion_blocker`,
  `l3_status`, `poc_tier`, `calibrated_severity_after_l3`, `l3_blocker_codes`, `human_override_required`,
  `human_override_reason`, `l3_evidence_summary`, `research_only:true`, `routing_allowed:false`). Empty/None → fails closed.
- `_facts()` now includes `candidate_id` (inert default-off).
- `evaluate()`: flag-guarded tail block appends `blocked_by_missing_l3_poc` for a High/Critical target lacking L3.
- `detail_overlay()`: flag-guarded read-only `out["l3"]`.

## Invariants preserved
`record_review` still never persists a false "ready" and never sets `submission_ready`/`routing_allowed=true`; overlay
append-only; `decide()` imported (single source of truth) and is side-effect-free.
