# P154 — What this taught the trainer

## Headline
The P153 selection lessons **worked**: applying the selection rules (deploy-light + unprivileged + crisp
mechanism + source-answerable reachability + feasible corrected-reference, deprioritizing privileged-only /
heavy-deploy / intent-dependent) led, on the first attempt, to the funnel's **first**
`reportable_candidate_needs_human_review` — without forcing it. The discipline did not lower the bar; it
*aimed* the effort.

## Five concrete lessons
1. **The corrected reference can be production code.** Instead of a hand-written "fixed" subclass, the
   prompt-`processExpiredLocks` path *is* the corrected behavior. Using real code as the reference is more
   faithful and removes a whole class of "did your fix introduce the delta?" doubt. Promote this pattern:
   *prefer an in-protocol corrected path over a synthetic one when one exists.*
2. **A control that proves the behavior is intended in one regime sharpens the finding in another.** The
   active-lock window (3× is correct) makes the post-expiry window (3× is wrong) unambiguous. Always test
   the *legitimate* regime alongside the *buggy* one.
3. **"Operator must do X" is a severity modulator, not necessarily a refutation.** Contrast P149 (intent
   *refuted* the external-theft framing → `needs_context`) with P154 (intent *expects* prompt processing,
   so it points *toward* a defect). The trainer rule: check whether intent **refutes** the mechanism or
   merely **bounds its magnitude** — only the former is an intent-ambiguity blocker.
4. **"User cannot self-remediate" is an aggravator worth capturing as a field.** The absence of a user-side
   unlock is what makes the incorrect distribution structural rather than the user's choice. Future
   selection should look for "victim cannot opt out" as a positive signal.
5. **Zero-sum proof beats magnitude proof.** Asserting `A_gain == B_loss` is a cleaner, harder-to-dispute
   impact statement than any single absolute number, and it survives parameter changes.

## What stayed disciplined
- Reaching `reportable_candidate_needs_human_review` did **not** mean claiming a bug: `reportable=unknown`,
  `submission_ready=false`, `routing_allowed=false`, and the severity grade + scope were explicitly handed
  to a human. The funnel produced a *candidate*, not a *verdict* — exactly the P153 thesis (promote,
  refute, downgrade, or stop on evidence).

## Funnel effect
First non-zero `reportable_candidate_needs_human_review` (1). The earlier four honest stop-types
(runtime_confirmed-but-privileged-only, runtime_refuted ×2, needs_context) now have a positive-terminal
sibling — the funnel has exercised its full outcome range honestly.
