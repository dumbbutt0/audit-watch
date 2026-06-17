# P253 — Verdict

## What the forensic established
- The completion failures (candidate existed / checkpoint fired / award exists / chain never completed)
  collapse into a **small recurring set of 5 reasoning operations** that explains **100% (13/13)** of the set
  by count and weighted, with the **top 3 = ~78%**, and the operations **recur across 6 distinct protocols**
  (salty, decent, vultisig, centrifuge, kleidi, munchables) → reusable, not contest-specific. The user's
  hypothesis is **confirmed**.
- The two dominant operations are **STATE_TRANSITION_SIMULATION** (instantiate the edge/first/empty state and
  step it) and **ADVERSARIAL_ACTOR_SUBSTITUTION** (replace the assumed honest actor with an attacker who
  chooses inputs / acts on-behalf). They carry the recovered Highs and ~61% of the lost weight.
- This re-confirms P252's diagnosis: the bottleneck is **performing the operation that completes the chain**,
  not **asking the question** — the checkpoints already ask; they don't perform.

## Verdict (exactly one)

# B — OPERATIONS_RECUR_BUT_SCAFFOLD_UNPROVEN

The recurring-operation hypothesis is **confirmed** (the forensic's primary deliverable succeeded), and the
evidence clearly points to an **exploit-chain construction scaffold** — a post-candidate-birth / pre-validation
procedure that *performs* these 5 operations — as the correct next architecture (NOT another checkpoint, NOT
another bug family, NOT cross-contract yet). So the design is warranted and sketched (SCAFFOLD_SKETCH.md).

It is **B, not A**, for one disciplined reason: **P252 is direct evidence that adding reasoning structure to a
prompt does not, by itself, produce chain completion on unseen code** (the checkpoints' questions gestured at
exactly these operations and still recovered nothing blind). The scaffold is more structure and better-aimed,
but P253's missing-steps are **reconstructed against known ground truth** — the forensic shows *which*
operations a human judge performed, not that a *scaffold can perform them blind*. Declaring A
(SCAFFOLD_WARRANTED as a confident build) would repeat the exact over-optimism that P250/P252 punctured.

Not C (the set clearly recurs). Not D (completion is the dominant in-scope failure mode here; coverage remains
a separate co-bottleneck for out-of-read-scope awards but is not what this set is about).

## Required next step (before any scaffold build)
A **targeted held-out test**: implement the scaffold's procedure as a *manual/scripted reasoning routine* (not
a wired production build) and run it **blind** on 2–3 of the completion-failure loci on an **unseen** contest,
measuring whether *performing* the 5 operations actually completes awarded chains the base hunt missed — the
same controlled, freeze-before-reveal discipline as P252. Build the production scaffold only if that test shows
the operations close the gap blind. If it does → A is earned and the scaffold is the architecture. If it
doesn't → the gap is deeper than procedure (the model can't perform the operation even when told to), which
would redirect toward training/tooling rather than scaffolding.

## Standing caveats
Training-confound (chains reconstructed against known awards); n=13 (3 primary + 10 corroborating);
single-LLM reconstruction. The forensic is a clean diagnosis; the architecture claim is a hypothesis to be
empirically tested next, not a promise.
