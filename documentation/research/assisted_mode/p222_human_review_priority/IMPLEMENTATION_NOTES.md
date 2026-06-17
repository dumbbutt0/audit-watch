# P222 — Implementation notes

## New: `scripts/human_review_priority.py`
Pure `evaluate_priority(record) -> {human_review_priority, human_review_reason_codes, reachability_class,
priority_explanation, priority_blockers, should_surface_above_noise}`. Tolerant accessor `_get()` reads from a
flat bundle or a synced record (including a nested `l3` dict). Inputs: `l3_status`, `impact_type`,
`reachability_class`, `conversion_outcome`/`mechanism_confirmed`, `dependency_mocks`, refutation notes,
`high_promotion_blocker`. It imports nothing from the severity path and emits none of the severity/submission keys.

## `scripts/sync_hunt_findings.py` (eb8c7d03 → …)
- `import human_review_priority as hrp`.
- In `build_bundle`, after the P221 reachability block: `impact_type = src("impact_type", l3rec.get("impact_type")
  or None, L3P)` (HARD RULE — artifact-backed). Then `prio = hrp.evaluate_priority({...})` built from the local
  `conv`, `l3rec`, `reachability_class`, `ddec.high_promotion_blocker`.
- Six fields added to the return dict and to `CARD_INJECT`, so they ride onto the synced record after
  `to_synced_finding()` — **`dashboard_sync.py` stays byte-identical**. The helper always returns a value, so
  every record carries the defaults (`NONE` / `[]` / `False`).
- Provenance: `human_review_priority` (when ≠ NONE) and `impact_type` recorded via `src(...)` against the L3 path.

## `output_research/l3_readiness/ZETA-04.json|ZETA-11.json`
Additive `impact_type` classifying the **already-proven** impact: ZETA-04 `core_safety_control_bypass`,
ZETA-11 `core_entry_exit_dos`. `attacker_model` and every existing field untouched → `decide()` byte-identical.

## `scripts/finding_detail.py` (8e4ab621 → …)
`build_verifier_evidence()` returns a new read-only `top_line_status` dict (banner + the four status lines +
mechanism/L3/reachability/priority + the unchanged `submission_ready`/`routing_allowed` echoes). Reads recorded
fields only; never calls `_sev_or_status` for severity and never flips a flag.

## `scripts/funnel.py` / `scripts/findings_overview.py`
- `build_finding_row()` whitelists `human_review_priority`, `human_review_reason_codes`, `reachability_class`,
  `should_surface_above_noise` from the synced record.
- `_load_funnel()` carries them onto overview rows; `_effective_rank()` (boost-only `min(base, boost)`) sorts
  HIGH→1.5 and MEDIUM→4.5, never demoting a row below its natural pipeline rank, never above reportable-ready
  (`glance_rank ≤ 1`). The sort key is `(effective_rank, glance_rank, track, subject)` (still stable).

## `scripts/dashboard.py`
`/api/findings` and `/api/candidates` gain an optional `human_review_priority: Optional[str] = None` query param
(read-only filter). No new POST; no submit/promote controls. Payloads keep `routing_allowed:false` /
`research_only:true`.

## `scripts/validate_hunt_sync_completion.py`
`_PRIORITY_VALUES` constant + three checks in `run_checks()`: (a) `human_review_priority` present and a valid
value — **`NONE` is a valid value, so validated against the value set, not `_present()`** (which rejects the
literal "none"); (b) HIGH/CRITICAL ⇒ `submission_ready is False`; (c) HIGH/CRITICAL ⇒ `routing_allowed is False`
and no silently-true `high_promotion_allowed` without L3 PASS.

## Gotcha fixed mid-build
First guard run failed with "human_review_priority missing" on the 8 `NONE` records because `_present("NONE")`
is False. Fixed by validating against `_PRIORITY_VALUES`. Also corrected `_effective_rank` from a flat
`return 4.5` (which demoted a strong MEDIUM row) to `min(base, boost)` (boost-only).
