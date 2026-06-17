# P210 — dashboard read-only L3 panel

Hash `1eb4e278` → `857d593a`. Single flag-guarded addition in the per-finding builder (~L398).

- When `AUDITWATCH_L3_READINESS` is set: compute `_l3_panel = submission_readiness_review.l3_evaluate(
  _load_l3_record(fid), tri.get("recommended_severity"))` (wrapped in try/except so the panel can never break the
  dashboard), and attach it as `findings_out[-1]["l3"]` ONLY when non-None.
- Flag OFF: `_l3_panel` stays None, the `l3` key is never added → dashboard JSON byte-identical to pre-P210.
- Display-only: shows threat ceiling / l3_status / poc_tier / high_promotion_allowed / blocker / evidence summary /
  human-override status. No submit/promote/demote controls; flips no canonical flag.
