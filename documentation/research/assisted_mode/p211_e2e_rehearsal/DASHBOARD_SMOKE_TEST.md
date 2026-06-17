# P211 — dashboard smoke test

Exercised the dashboard's L3 computation path (`submission_readiness_review.l3_evaluate(_load_l3_record(fid), severity)`
+ the P210 attach guard) flag off vs on.

- **Flag OFF:** `_l3_panel` is None → no `l3` key attached to any finding (dashboard JSON byte-identical to pre-P210).
- **Flag ON:** every rehearsal candidate gets a read-only `l3` panel: `high_promotion_allowed`, `high_promotion_blocker`,
  `l3_status`/`poc_tier`, `calibrated_severity_after_l3`, `l3_evidence_summary` (poc_path/actual/control). Each panel
  carries `research_only:true`/`routing_allowed:false`.
- **Read-only:** the panel is a data dict only — no submit/promote/demote controls; flips no canonical flag.
- **Medium unaffected:** a Medium target yields `{"applies": false}` (no High gating in the panel).

(`dashboard.py` hash `857d593a` unchanged during P211 — the path was exercised via the same helper the dashboard calls.)
