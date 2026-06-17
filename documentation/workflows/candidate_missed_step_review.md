# Workflow Spec — Candidate Missed-Step Review (RESEARCH-ONLY, un-wired)

> No dynamic-workflow runtime exists in this repo, so this workflow is a **spec + deterministic stub**
> (`scripts/investigation/missed_step_workflow_stub.py`). In real use the verifier roles are **isolated agents** driven by
> the P78 skills (`/audit-candidate-verification`, `/adversarial-bundle-review`); the stub encodes the same fail-closed
> synthesis so the workflow is testable. It never routes and never calls a production gate.

## Purpose
Given a P77 investigation bundle, fan out **isolated verifier roles** and synthesize a **promotion-safe** decision. A
candidate cannot reach `POC_REQUIRED` / `READY_FOR_HUMAN_REVIEW` unless every critical check passes and (for READY) an
adversarial review PASSed. The author of a bundle does not judge its own promotion.

## Roles (each isolated; returns `{verifier_name, status PASS|FAIL|UNKNOWN, source_evidence, missed_steps, blocking_reason, recommended_status}`)
- **A. Reachability Verifier** — source/entrypoint/call-path exist; caller can reach the path; helper/modifier/library
  context resolved or marked unknown. (unresolved → UNKNOWN → NEEDS_CONTEXT)
- **B. Defense-Ledger Verifier** — all relevant defenses classified; any `blocks_candidate` → FAIL (REJECTED); any
  critical/relevant defense `unknown`/`source_unavailable` → UNKNOWN (NEEDS_CONTEXT); `irrelevant` needs only its reason.
- **C. Source-Falsifier** — runs the 10 falsifiers; any success → FAIL (REJECTED) with source evidence; falsification not
  performed → UNKNOWN.
- **D. Invariant & Impact Verifier** — explicit broken invariant + concrete `transaction_sequence` + measurable impact;
  severity not inflated; PoC need clear. Missing any → FAIL.
- **E. Provenance & Transition Verifier** — legal `state_trace` (no detector→finding shortcut), research/review-only flags,
  no production routing, no forbidden finality language. (reuses `hygiene_validate.py`)
- **F. Synthesizer** — fail-closed merge.

## Synthesizer rules (fail-closed)
- Any FAIL whose recommendation is REJECTED → `final_status = REJECTED`.
- Any other FAIL or UNKNOWN → `final_status = NEEDS_CONTEXT`.
- `POC_REQUIRED` only if attacker sequence + broken invariant + impact exist (and `poc_needed`).
- `READY_FOR_HUMAN_REVIEW` only if source-falsification passed, all critical fields source-backed, **and adversarial review
  = PASS**.
- Never emit: confirmed bug · valid finding · submission ready · ready to submit · auto-submit · exploitable confirmed.

Returns `{final_status, blocking_checks, missed_steps, required_fixes, promotion_allowed, reason}`.

## Meaning of the promotion states (restated)
- `POC_REQUIRED` = permission to create a **local** PoC task only. Not a severity/validity/submission verdict.
- `READY_FOR_HUMAN_REVIEW` = the investigation bundle is ready for a **human** to review. Not a finding, not submission.

## Run
```
python3 scripts/investigation/missed_step_workflow_stub.py --bundle <bundle.json> [--review <review.json>]
python3 scripts/investigation/missed_step_workflow_stub.py --self-test
```
All artifacts: `research_only:true review_only:true is_gate:false routes_in_production:false routed_manifest_ids:[]`.
