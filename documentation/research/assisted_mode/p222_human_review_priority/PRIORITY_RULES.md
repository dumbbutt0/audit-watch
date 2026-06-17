# Priority rules (P222)

Pure, deterministic. Implemented in `scripts/human_review_priority.py::evaluate_priority(record)`. Reads only
display/evidence fields; writes only the six priority fields; never touches severity or safety flags.

## Inputs (read-only)
- `conversion_outcome` / `mechanism_confirmed`
- `l3_status` (PASS / FAIL / NEEDS_HARNESS / NOT_ATTEMPTED / HUMAN_OVERRIDE)
- `impact_type` (artifact-backed classification over the *proven* impact; absent ⇒ rule can't fire)
- `reachability_class` (see `REACHABILITY_CLASS_MODEL.md`)
- refutation signals: `l3_status=FAIL`, `reachability_class=SOURCE_REFUTED`, `"refut"` in source notes
- `dependency_mocks` (to exclude mock-created vulns)

## Outputs
`{human_review_priority, human_review_reason_codes, reachability_class, priority_explanation,
priority_blockers, should_surface_above_noise}`. Defaults: `NONE` / `REACHABILITY_UNKNOWN` / `false`.

## Qualifying impact types
`core_safety_control_bypass · emergency_pause_bypass · core_entry_exit_dos ·
cross_chain_message_invariant_bypass · protocol_accounting_invariant_violation · fund_lock_or_failed_refund`.

## Qualifying reachability (for the HIGH lane)
`TRUSTED_SYSTEM_ACTOR_REACHABLE · PROGRAM_ACCEPTED_ACTOR_REACHABLE · KEEPER_OR_RELAYER_REACHABLE ·
ADMIN_OR_OWNER_REACHABLE · PRIVILEGED_ONLY_REACHABLE`.

## The HIGH rule
`human_review_priority = HIGH` and `human_review_reason_codes ⊇ {PROGRAM_THREAT_MODEL_DECISION_REQUIRED}`
**iff all**:
1. `mechanism_confirmed = true` **OR** `conversion_outcome ∈ {CLEAN_HIT, STRONG_PARTIAL}`;
2. `l3_status = PASS`;
3. `impact_type ∈ qualifying impact types`;
4. `reachability_class ∈ qualifying reachability`;
5. **not refuted** (`l3_status ≠ FAIL`, `reachability_class ≠ SOURCE_REFUTED`, no `"refut"` in notes) **and**
   `dependency_mocks ≠ creates_vulnerable_condition`.

Additional reason codes attach by evidence: `CORE_SAFETY_CONTROL_BYPASS` (impact_type ∈
{core_safety_control_bypass, emergency_pause_bypass}), `TRUSTED_SYSTEM_ACTOR_REACHABLE` /
`L3_PASS_BUT_PRIVILEGED_TRIGGER` (privileged/trusted reachability). When HIGH, the helper also marks
`should_surface_above_noise=true` and leaves `submission_ready=false`, `routing_allowed=false`,
`high_promotion_allowed` untouched (L3-owned); `priority_blockers` carries the existing submission blocker so
it stays visible.

## The MEDIUM / LOW / NONE fall-through
- **MEDIUM** — `l3_status=PASS` + qualifying `impact_type`, but the HIGH reachability gate fails (e.g.
  `REACHABILITY_UNKNOWN`) or the result is a **wrong-mechanism partial** / scope-dependent. Reason codes:
  `L3_PASS_BUT_SCOPE_DECISION_REQUIRED`, `NEEDS_PROGRAM_RULE_INTERPRETATION` (+ `NEEDS_SEVERITY_POLICY_DECISION`
  for availability/DoS). `should_surface_above_noise=true`.
- **LOW** — a real residual after an impact was refuted (e.g. a missing-modifier code fact whose theft claim
  failed L3). Reason: `LOW_CONFIDENCE_NOISE`. `should_surface_above_noise=false`.
- **NONE** — refuted with no residual, no-impact, self-inflicted, mock-created, code-quality-only, or
  static-only with no L3 PASS. Default.

## Never HIGH (hard exclusions)
static-only / no L3 PASS · ordinary admin misconfig with no core-invariant impact · `SELF_INFLICTED_ONLY` ·
source-refuted / `l3_status=FAIL` / `"refut"` in notes · code-quality-only · mock-created vulns
(`dependency_mocks=creates_vulnerable_condition`) · no-impact · `UNPRIVILEGED_REACHABLE` (already reportable
through the normal path) · `REACHABILITY_UNKNOWN`.

## Applied to the current corpus
| candidate | l3_status | impact_type | reachability_class | → priority | why |
|-----------|-----------|-------------|--------------------|-----------|-----|
| ZETA-04 | PASS | core_safety_control_bypass | TRUSTED_SYSTEM_ACTOR_REACHABLE | **HIGH** | all 5 conditions met |
| ZETA-10 | FAIL | (none) | UNPRIVILEGED_REACHABLE | **LOW** | theft refuted; residual missing-nonReentrant code fact |
| ZETA-11 | PASS | core_entry_exit_dos | REACHABILITY_UNKNOWN | **MEDIUM** | qualifying impact but reachability unknown + wrong-mechanism partial |
| ZETA-07 | PASS | (none) | (derived, non-qualifying) | **NONE** | no qualifying impact_type / reachability; privileged precondition |
| H5-style | PASS | (any) | UNPRIVILEGED_REACHABLE | **NONE** | unprivileged ⇒ reportable through normal path, not the lane |
