# P222 — ZETA backfill results

Regenerated via `run_hunt_sync_hook.py --phase P215 --audit zetachain-2023-10-holdout --workspace …` →
**exit 0, completion guard PASS, 12 records, completeness 90%, all_safety_ok=True**.

| candidate | l3_status | impact_type | reachability_class | human_review_priority | reason codes | surface | submission_ready | routing_allowed | high_promotion_allowed |
|-----------|-----------|-------------|--------------------|----------------------|--------------|---------|------------------|-----------------|------------------------|
| ZETA-04 | PASS | core_safety_control_bypass | TRUSTED_SYSTEM_ACTOR_REACHABLE | **HIGH** | PROGRAM_THREAT_MODEL_DECISION_REQUIRED, CORE_SAFETY_CONTROL_BYPASS, L3_PASS_BUT_PRIVILEGED_TRIGGER, TRUSTED_SYSTEM_ACTOR_REACHABLE | True | False | False | False |
| ZETA-10 | FAIL | (none) | UNPRIVILEGED_REACHABLE | **LOW** | LOW_CONFIDENCE_NOISE | False | False | False | False |
| ZETA-11 | PASS | core_entry_exit_dos | REACHABILITY_UNKNOWN | **MEDIUM** | L3_PASS_BUT_SCOPE_DECISION_REQUIRED, NEEDS_PROGRAM_RULE_INTERPRETATION, NEEDS_SEVERITY_POLICY_DECISION | True | False | False | False |
| ZETA-07 | PASS | (none) | REACHABILITY_UNKNOWN | **NONE** | — | False | False | False | False |

All 12 records carry the six priority fields (defaults `NONE` / `[]` / `False` where the rule doesn't fire).

## Acceptance check
- **ZETA-04** — HIGH; reason codes ⊇ {PROGRAM_THREAT_MODEL_DECISION_REQUIRED, CORE_SAFETY_CONTROL_BYPASS,
  L3_PASS_BUT_PRIVILEGED_TRIGGER}; `submission_ready=false`, `routing_allowed=false`, `high_promotion_allowed=false`. ✅
- **ZETA-10** — LOW (not HIGH) after L3 refutation of the theft claim. ✅
- **ZETA-11** — MEDIUM (l3 PASS + core_entry_exit_dos, but REACHABILITY_UNKNOWN + wrong-mechanism partial vs the
  claimed theft); the wrong-mechanism partial is reflected in the reason codes + the L3 record's
  `source_validity_notes`. ✅
- **ZETA-07** — not high priority (no qualifying impact_type; privileged GAS_LIMIT precondition). ✅
- **H5-style unprivileged** — fixture-verified: `UNPRIVILEGED_REACHABLE` ⇒ NONE, stays out of the lane and
  reportable through the normal path. ✅

## Mirror diff (vs the P222 START baseline, md5 ac8978df)
Top-level non-additive drift: **NONE**. The only changes are the six additive priority keys (12 records),
`impact_type` (ZETA-04/11 only), and the nested `_field_provenance` gaining those keys — no existing value
modified or removed.
