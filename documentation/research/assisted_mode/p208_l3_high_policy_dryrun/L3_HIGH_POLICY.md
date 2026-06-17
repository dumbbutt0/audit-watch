# L3 HIGH Policy (dry-run, research-only, un-wired)

**Status:** dry-run severity policy. It does **not** submit, route, promote, or demote any real finding, and does
**not** modify canonical labels or answer keys. It is an advisory overlay computed from evidence fields.

## 1. Threat ceiling vs final severity
The deep-trace verdict (`CRITICAL/HIGH/MEDIUM_THREAD`) is a **worst-case threat ceiling** by design (see P199), not a
calibrated final severity. A candidate's final HIGH status must be *earned* by realized-impact evidence, not inherited
from the ceiling. This policy is the calibration gate between ceiling and reported severity.

## 2. PoC tiers (L1 → L3)
- **L1_STATIC_TRACE** — static reachability/capability argument only (the deep-trace thread). Necessary, not
  sufficient for HIGH.
- **L2_UNIT_HARNESS** — a unit/property harness exercising the logic in isolation (some mocks). Supports magnitude
  but may not prove end-to-end realized impact.
- **L3_REAL_CONTRACT_POC** — the real contract(s) run unmodified, only external deps mocked, **honest custody**,
  attacker-controlled tx, **measured** material outcome with before/after state and a control case. This is the HIGH
  bar (P204/P207 standard).
- **HUMAN_EQUIVALENT** — a human reviewer certifies reproducible evidence equivalent to L3, with written rationale.
- **NONE** — no PoC.

## 3. Required evidence fields
`l3_status` ∈ {PASS, FAIL, NEEDS_HARNESS, NOT_ATTEMPTED, HUMAN_OVERRIDE} · `poc_tier` (above) · `poc_path` ·
`poc_command` · `poc_result` · `actual_delta` · `expected_delta_or_control` · `affected_asset_or_state` ·
`attacker_model` · `victim_or_protocol_loss` · `magnitude_basis` · `source_validity_notes` · `dependency_mocks` ·
`production_source_modified` (bool) · `high_promotion_allowed` (bool, derived) · `high_promotion_blocker`.

## 4. HIGH_CONFIRMED promotion rule (derived `high_promotion_allowed`)
`high_promotion_allowed = true` **iff ALL** hold:
1. `l3_status ∈ {PASS, HUMAN_OVERRIDE}`;
2. `affected_asset_or_state` is concrete (named asset/slot/balance/role);
3. material delta demonstrated (`actual_delta` non-trivial AND `victim_or_protocol_loss` present AND
   `magnitude_basis` given);
4. `attacker_model` is permissionless OR matches the program-accepted threat model;
5. `production_source_modified == false`;
6. mocks do **not** create the vulnerable condition (`dependency_mocks` are external-only / `source_validity_notes`
   assert the bug is in real code);
7. a control case or expected-vs-actual comparison is present (`expected_delta_or_control` non-empty).

Otherwise `high_promotion_allowed = false` with a specific `high_promotion_blocker`.
For `HUMAN_OVERRIDE`, a written rationale in `source_validity_notes` (or `poc_result`) is mandatory; conditions 2–7
still apply.

## 5. Demotion / Needs-Harness mapping (`calibrated_severity`)
- valid mechanism without realized High impact → `MEDIUM_OR_LOWER_CALIBRATED`;
- static capability-only High (l3 NOT_ATTEMPTED / poc_tier L1/NONE) → **not reportable as High**;
- unproven magnitude (no `magnitude_basis`) → `NEEDS_HARNESS_FOR_SEVERITY`;
- DoS / griefing / precision / local / bounded impact → **Medium** unless L3 proves permanent material loss or
  insolvency;
- `l3_status == FAIL` or source-refuted → blocked from High (Medium/invalid per mechanism).

## 6. Human override
Allowed only with a written rationale and the same concrete-asset / material-delta / control requirements as an L3
PASS. Recorded as `l3_status == HUMAN_OVERRIDE`. No silent overrides.

## 7. Non-submission guarantee
This policy computes advisory fields only. It NEVER sets `submission_ready`/`routing_allowed`, never promotes/demotes
a canonical finding, and never submits. A HIGH report package still requires human review (see
`SUBMISSION_READINESS_LINKAGE.md`).
