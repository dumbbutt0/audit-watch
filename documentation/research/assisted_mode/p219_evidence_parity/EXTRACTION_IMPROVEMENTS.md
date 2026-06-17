# P219 — EXTRACTION IMPROVEMENTS

Two additive, read-only edits. `dashboard_sync.py` unchanged (new card fields injected by the wrapper after
`to_synced_finding`).

## `scripts/sync_hunt_findings.py` (8d8a3203 → new)
- `_confirm_index(audit)`: load per-candidate `reachability_status` from `confirm/reachability_analysis.json`.
- `_LOSS_TYPE`: impact_class → human loss-type label.
- `build_bundle`: rewritten with a `src()` provenance recorder enforcing the HARD RULE; now extracts:
  - reachability_verdict (confirm), PoC actual/expected/control/value-delta + corrected_reference_type (L3),
    impact who_loses/asset_or_value/loss_type (L3 + impact_class), 5 derived red_flags each citing evidence,
    richer evidence_backup (confirm + report-package + harness), `_field_provenance` map, `who_gains` left unknown.
  - post-score scorecard verdict kept ONLY in scoring_note/last_reviewer_note (never a blind field).
- `main`: passes `confirm_idx`; injects the card-consumed top-level fields
  (`vulnerable_output/corrected_output/control_case/runtime_delta/corrected_reference_type/reachability_verdict/
  who_loses/who_gains/asset_or_value/loss_type/scoring_note/_field_provenance`) onto the synced record so the detail
  renderer reads them — without changing `dashboard_sync.py`.

## `scripts/finding_detail.py` (f12aa8d3 → new)
- `build_verifier_evidence`: additive — prefer INLINE `raw.who_loses/who_gains/loss_type/asset_or_value` over the text
  heuristic when present. The PoC section already read `raw.vulnerable_output/corrected_output/control_case/runtime_delta`
  (no edit needed). **Never** touches severity (`_sev_or_status`), `submission_ready`, or `routing_allowed`.

## What was NOT done (kept honest)
- No blind discovery rerun (REPLAY_MODE). No new harnesses. `novelty_duplicate` stays unknown (no source). who_gains
  unknown for all Zeta (no beneficiary named in any artifact). Executed-PoC fields stay absent for NEEDS_HARNESS
  candidates — not fabricated.
