# P100 — Assisted-Mode Dashboard Review & Metrics Summary

**Date:** 2026-06-03 · **Type:** dashboard review + metric verification + reporting (no blind eval, no submission,
no machinery change). Verifies the product state is accurate, readable, and safe for human operation.

## Current operating model
Audit-Watch is a **human-gated validation, PoC-handoff, submission-readiness, and outcome-tracking** system. A
human (or external tool) supplies the candidate invariant; Audit-Watch validates it from source, helps reproduce
an executable PoC, assembles a platform-neutral submission package, and tracks human-recorded outcomes. It does
**not** submit, does **not** decide scope/duplicate, and is **not** an autonomous blind-discovery engine. Full
workflow: `runbook.md`; human gate: `human_final_gate.md`; positioning: `autonomous_blind_discovery_ceiling.md`.

## Current dashboard truth (`/api/funnel`, `/funnel`)
- Every row exposes (top-level): `candidate_id`, `subject`, `source_mode`, `supplied_by`, `finding_title`,
  `pipeline_status`, `poc_status`, `submission_status`, `human_final_gate`, `submitted`, `outcome`,
  `claimed_severity`, `awarded_severity`, `duplicate_check`, `scope_check`, `severity_check`, `final_human_gate`,
  `poc_command`, `blocker_reason`, plus the `submission` object + `artifact_links` (package paths).
- **`READY_FOR_HUMAN_REVIEW` does not imply `SUBMITTED`.** SUBMITTED is shown only from an explicit human outcome
  record (`submitted=true`); it is never inferred from submission readiness.
- Blind vs assisted records are visually distinguishable (Source column: `blind` plain pill, `assisted` green +
  `invariant ✓`). Historical blind records render unchanged.
- The "Human gate / outcome" column shows `human_final_gate`, a `not submitted` note, the `outcome`, and the
  scope/duplicate/severity human-review sub-checks.

## Proven artifacts (both pending human review, not submitted)
| Finding | source_mode | poc_status | submission | human_final_gate | submitted | outcome |
|---|---|---|---|---|---|---|
| Vultisig H-01 (`ILOPool.claim` shared-position fee siphon) | blind | REPRODUCED | READY_FOR_HUMAN_REVIEW | PENDING | false | pending |
| SecondSwap M-11 (`maxSellPercent` self-purchase bypass) | assisted (human-supplied invariant) | REPRODUCED | READY_FOR_HUMAN_REVIEW | PENDING | false | pending |

## Metrics table (verified `funnel.load_records()`)
| Metric | Value |
|---|---|
| total funnel records | 8 |
| blind records | 7 |
| assisted records | 1 |
| PoC reproduced (total, `poc_reproduced_total`) | 2 |
| submission ready for human review | 2 |
| human_final_gate = PENDING | 8 |
| submitted count | 0 |
| accepted count | 0 |
| duplicate count | 0 |
| rejected count | 0 |
| pending outcome count | 8 |
| ready_for_human_review by source_mode | blind: 1, assisted: 1 |
| reproduced → submission-ready | 2 |
| assisted → reproduced | 1 |
| submission-ready → submitted | 0 |
| severity-FP (post-gate) | 0 |
| outcome records loaded | 2 |

> Note: the legacy `pocs_reproduced` metric counts records *still at* the `POC_REPRODUCED` stage (= 0 here,
> because both reproduced PoCs advanced to submission-ready). The human-facing count is `poc_reproduced_total` = 2.

## What is safe to claim
- The assisted-mode workflow exists and runs end-to-end.
- An outcome recorder exists and enforces reject-first invariants.
- The dashboard distinguishes blind and assisted sources.
- Two reproduced PoC packages are **ready for human review**.
- **No submission has been recorded** (`submitted_count = 0`).
- Human scope / duplicate / severity checks are **still pending**.

## What is NOT safe to claim
- Autonomous blind discovery is reliable. *(It is not — see the ceiling note; arc stopped at P97.)*
- Any report has been submitted.
- Any finding has been accepted / awarded.
- Scope or duplicate checks are complete.
- Severity is program-final.
- Any bounty outcome is known.

## Next human actions
1. Review the Vultisig H-01 and SecondSwap M-11 packages (`submission_package/` + evidence).
2. Perform scope and duplicate / publicly-known checks.
3. Re-run the PoC commands locally.
4. Record `APPROVED_TO_SUBMIT` or a `DO_NOT_SUBMIT_*` decision via `scripts/assisted/record_assisted_outcome.py`.
5. Only then may a report be submitted **manually** by the human.

## Next engineering actions (optional, low priority)
- Per-source severity-FP / conversion breakdowns if more assisted candidates accrue.
- A small per-candidate "human checklist" view linking the package files inline.
- Continue feeding `lessons_learned` into templates/prompts (never into historical scores).
