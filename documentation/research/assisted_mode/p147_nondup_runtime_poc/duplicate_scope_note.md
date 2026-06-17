# P147 — Duplicate & Scope Note

## Scope / duplicate classification: **duplicate_unknown**
- `centrifuge-2023-09-holdout` is a **holdout** with **no local answer key** (verified: no `answer_key.md` under
  the audit). So there is no local record establishing this as a known/awarded finding → `duplicate_status =
  duplicate_unknown`.
- This is the deliberate contrast with B1 (noya H-03) and B5 (blackhole M-04), which are `duplicate_known` (in
  their eval answer keys). P147's panel row is the first runtime-confirmed row that is **not** `duplicate_known`.

## Honest non-claims
- **No novelty claim.** `duplicate_unknown` means "no local record," NOT "novel." The UserEscrow allowance-proxy
  concern matches a recognized Centrifuge finding class; P147 does not assert discovery or award.
- **No submission.** `submission_ready=false`; `requires_human_review=true`; `requires_poc_review=true`.
- **Intent-dependent.** The `receiver != destination` path is documented "additional protection," so validity /
  severity is explicitly deferred to human review (see limitations.md).

## Why this still satisfies the phase
The phase asked for a **non-duplicate** corpus item taken to runtime PoC. `duplicate_unknown` (no local duplicate
record) + a real-contract runtime confirmation + a panel row carrying that status, with the prompt baseline
preserved, satisfies it honestly — without overclaiming novelty or submission-readiness.
