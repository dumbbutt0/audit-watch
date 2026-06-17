# P249 — Part A: Architecture (why this is a checkpoint, not a detector)

The accounting checkpoint is an **examine-time reasoning aid**, not a detector. The distinction is enforced
in code and unit-tested.

| | Detector (e.g. P237/P238/P242 lenses) | **Accounting Checkpoint (P249)** |
|---|---|---|
| Output | candidate findings with a verdict | **interrogative reasoning records** |
| Carries severity / confidence | yes | **never** (`severity:null`, `confidence:null`) |
| Concludes vulnerability | yes (that's its job) | **never** (`concluded:false`, `concludes_vulnerability:false`) |
| Emits findings | yes | **no** (`emits_findings:false`) |
| Per-fire meaning | "this IS suspicious / a finding" | "answer 6 questions before you move on" |
| Adjudication | the detector decides | the **existing precision pipeline** decides, on the operator-constructed candidate |
| FP exposure | each fire is a precision liability | a fire is a *question*, not a claim → no precision liability |

## What it does (the 4 steps)
1. **Observe** a suspicious accounting *shape* (one of 5 families A1–A5) — broad on purpose; observing ≠
   concluding.
2. **Emit a structured `ACCOUNTING_CHECKPOINT` record** with the six mandatory questions and EMPTY hypothesis
   fields (`exploit_hypothesis:""`, `conservation_actual:""`, `potential_winner/loser:""`).
3. **Force candidate construction:** the operator must answer the six questions; only an answer that shows a
   plausible value path fills `exploit_hypothesis` → that filled record IS the constructed candidate.
4. **Route, don't conclude:** the constructed candidate enters the EXISTING precision pipeline (2.5 merge →
   ICE → multi-pass → FP-check → pre-submission gates → triage). The checkpoint routes nothing itself
   (`routes_in_production:false`, `routed_manifest_ids:[]`).

## Why this prevents reasoning collapse (the P248 funnel)
P248 found candidates die at two stages: Observed→Generated-Candidate (39%) and Generated-Candidate→
Exploit-Chain (61%). The checkpoint attacks both: the *observation + the six questions* force a candidate to
be born at the suspicious accounting shape (stage 1), and the questions ("can value be created/destroyed/
double-counted/another actor deprived/rounding wrong/repeat amplify?") are exactly the exploit-chain skeleton
(stage 2). It does not supply the *answer* — it supplies the *obligation to reason*.

## The hard invariant (stop condition)
If the only way to make the checkpoint useful were to let "firing == concluding," it would be a detector and
P249 fails to C. It does not: the runner asserts every record has `severity is None and concluded is False`,
the unit test `test_checkpoint_never_concludes_or_sets_severity` enforces it, and all 234 records produced in
the replay carried empty hypotheses and null severity (Part D). Firing is interrogative; conclusion is the
pipeline's job.
