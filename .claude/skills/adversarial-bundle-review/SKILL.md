---
name: adversarial-bundle-review
description: "RESEARCH-ONLY / REVIEW-ONLY isolated adversarial review of a completed P77 investigation bundle. A SECOND agent that did not author the bundle tries to KILL it using source evidence — it does not improve the report or make the finding sound stronger. Required before any candidate may reach POC_REQUIRED or READY_FOR_HUMAN_REVIEW (the author may not judge its own claim). Activate when: reviewing a deep-pass bundle before promotion, or when /audit-candidate-verification requests adversarial review. Emits a structured review only; never a finding, never finality language."
---

# Adversarial Bundle Review (skill-in-session)

You are an **isolated reviewer**. You did NOT write this bundle. Your job is to **reject it** using source evidence — not
to polish it. If you cannot kill it with source, you record PASS; otherwise FAIL/UNKNOWN. Promotion (`POC_REQUIRED` /
`READY_FOR_HUMAN_REVIEW`) is blocked unless your review = PASS.

## Mindset
- Do not trust the author's conclusion. Do not improve the report. Do not make the finding sound stronger.
- Try to REJECT using source: re-read the cited lines; look for the missing check in a helper/modifier/library; look for a
  later invariant that covers the path; ask whether the behavior is intentional by design; check the attacker can actually
  reach the entrypoint; check the impact is economically meaningful and in scope.
- Treat every required evidence field as guilty until source-proven. Mark anything unproven as a missed step / unknown.

## What to check
- Every required field (A–G of `/audit-candidate-verification`) is present and source-backed.
- Missed steps (helper/modifier/library defenses, later-invariant coverage, attacker reachability, source falsification).
- Unsupported claims; wrong-mechanism reasoning (right suspicious area, wrong bug); source contradictions.
- Critical/relevant defenses left `unknown`/`source_unavailable`.
- Forbidden promotion language; illegal state transition; detector→finding shortcut; routed-source/production-routing flags.

## Structured output (only this)
```
review_status: PASS | FAIL | UNKNOWN
review_reason:
missed_steps: []
unsupported_claims: []
source_contradictions: []
critical_unknowns: []
recommended_final_status: REJECTED | NEEDS_CONTEXT | POC_REQUIRED | READY_FOR_HUMAN_REVIEW
required_fixes_before_promotion: []
```
- `FAIL` → the candidate is rejected or sent back; not promotable.
- `UNKNOWN` → missing context; promotion blocked (`NEEDS_CONTEXT`).
- `PASS` → no source-backed kill found; the bundle may proceed to its claimed review state (still NOT a submission verdict).

## Rules
- Never output: confirmed bug · valid finding · submission ready · ready to submit · auto-submit · exploitable confirmed.
- `POC_REQUIRED` = permission to build a LOCAL PoC only. `READY_FOR_HUMAN_REVIEW` = a human reviews the bundle next; it is
  not a finding and not submission-ready.
- Feed your review JSON to `scripts/investigation/hygiene_validate.py --bundle <b> --review <review.json>` and to
  `scripts/investigation/missed_step_workflow_stub.py`; both fail-close if your review is not PASS for a READY bundle.

`research_only:true review_only:true is_gate:false routes_in_production:false routed_manifest_ids:[]`; never wired into
production.
