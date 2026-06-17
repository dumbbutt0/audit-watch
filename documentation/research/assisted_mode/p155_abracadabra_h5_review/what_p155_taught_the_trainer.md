# P155 — What this taught the trainer

## Headline
A reportability review can **sharpen** a candidate (bound its severity, surface caveats) without
**refuting** it — and that is a distinct, valuable outcome from the P148/P152 refutations and the P151/P149
blocks. P155 kept H5 as a reportable candidate but converted "severity unknown" into "Medium, bounded by
trusted-operator liveness, with two named scope/novelty caveats for the human."

## Five lessons
1. **Separate the four axes, literally.** Mechanism (proven, untouched) ≠ severity (Medium) ≠ scope
   (trusted-operator) ≠ novelty (unknown). The review changed only the latter three; `runtime_status`
   stayed `runtime_confirmed`. Keeping them in separate fields is what let the verdict be precise.
2. **Intent ambiguity is not automatically a block.** P149's ambiguity *refuted the attacker model* →
   `needs_context`. P155's ambiguity only concerns *whether the loss is an accepted tradeoff* → it bounds
   severity but the attacker model survives. Trainer rule: ask whether the ambiguity attacks the *mechanism*
   or merely the *grading*.
3. **"Trusted operator" has three different effects — name which one.** It can bound severity, block
   reportability, or be a pure design choice. Here it *bounds* (real third-party loss, no self-remediation),
   so it is neither a free pass nor a kill. Forcing the choice among the three prevents lazy "it's just an
   admin thing" dismissals.
4. **Check provenance/lineage as part of novelty.** The contract's own NatSpec ("Based from Convex
   CvxLockerV2 / Curve") is simultaneously intent evidence *and* a public-known caveat. Inherited patterns
   carry inherited (and possibly already-reported) issues. Always read the "@author / based from" lines.
5. **An empty local record + a public contest = duplicate_unknown, not novel.** The project previously
   read this very C4 report (Phase 14c) yet recorded only an unrelated finding (M-10). That is *weak*
   evidence, not novelty. The honest output is `duplicate_unknown` with an explicit "external check
   required," never an inferred "novel."

## Discipline preserved
No over-promotion: `submission_ready=false`, `routing_allowed=false`, severity bounded (not inflated),
novelty left unknown, and an explicit alternative reading (`blocked_by_trusted_operator_scope`) documented
for the human. The review made the candidate *more honest*, not *more confident*.
