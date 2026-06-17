# P251 — Part A: Architecture (state-transition checkpoint; mirrors P249)

The STATE_TRANSITION checkpoint is an examine-time **reasoning aid**, not a detector. It is the second
checkpoint, built on the validated P249 accounting template, for the highest-absolute-recovery reasoning
family (P247/P248): state-machine bugs where the system reads the right code but fails to *adversarially trace
the state transition*.

| | Detector | **State-Transition Checkpoint** |
|---|---|---|
| Output | candidate findings with a verdict | **interrogative STATE_TRANSITION_CHECKPOINT records** |
| severity / confidence | yes | **never** (`severity:null`, `confidence:null`) |
| concludes vulnerability | yes | **never** (`concluded:false`, `concludes_vulnerability:false`) |
| emits findings | yes | **no** (`emits_findings:false`) |
| per-fire meaning | "this IS a bug" | "answer 8 questions: adversarially trace this transition" |
| adjudication | the detector | the **existing precision pipeline**, on the operator-constructed candidate |

## The 4 steps
1. **Observe** a state-transition *shape* (one of 5 families S1–S5) — broad on purpose; observing ≠ concluding.
2. **Emit** a `STATE_TRANSITION_CHECKPOINT` record: the 8 questions + EMPTY hypothesis fields (pre_state,
   post_state, repeated_action_effect, affected_actor, invariant_after_transition, exploit_hypothesis).
3. **Force candidate construction:** the operator answers the 8 questions; only an answer showing a plausible
   state-machine exploit fills `exploit_hypothesis` → that filled record IS the constructed candidate.
4. **Route, don't conclude:** the candidate enters the EXISTING precision pipeline. The checkpoint routes
   nothing (`routes_in_production:false`, `routed_manifest_ids:[]`).

## Why this attacks the P248 funnel
P248 located the loss at Observed→Generated-Candidate (39%) and Generated-Candidate→Exploit-Chain (61%, where
the reasoning Highs are). State-transition was the single highest-absolute-recovery cluster. The 8 questions
are the adversarial state-trace skeleton — "can an attacker choose it / repeat it / overwrite another's state
/ grow an unbounded set / make two states true / a failure branch still mutates / a time-window change breaks
existing state / who is harmed." Asking them at the observed locus forces both candidate birth and chain
construction. The checkpoint supplies the obligation to reason, never the answer.

## Hard invariant (stop condition)
If "firing == concluding," it is a detector and P251 fails to C. It does not: the runner asserts every record
has `severity is None and concluded is False`; the unit test `test_checkpoint_never_concludes_or_sets_severity`
enforces it; and across all replay/FP runs (munchables/kleidi/spectra/decent) **0 records carried a
conclusion**. Firing is interrogative.
