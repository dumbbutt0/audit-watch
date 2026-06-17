# P252 — Verdict

## The decisive question (per the phase's honesty rule)
> Did the checkpoint **create or complete an awarded-equivalent exploit chain on unseen code?**

**No.** CHECKPOINT_ONLY awarded-equivalent = **0**; genuine BASE_PLUS_CHECKPOINT (checkpoint materially
created/completed an awarded chain) = **0**. The one new checkpoint-born candidate (CP-1, DAO SEND_SALT
skip-but-finalize) is real but **not awarded**. The awarded recoveries (M-06, M-11, M-01-partial) were
BASE_ONLY — Arm A already had them; the checkpoints' firing on those loci was redundant.

## Verdict (exactly one)

# B — ARCHITECTURE_VALIDATED_BUT_LIFT_UNPROVEN

No recall lift (Arm A = Arm B = 5.1% weighted, 0/6 High), but:
- **Architecture validated on unseen code:** both checkpoints emit 0 findings / 0 severity / 0 conclusions
  (re-verified), are FP-safe, and **fired precisely on the correct awarded-finding loci** (castVote → M-06/
  M-11; `_increaseUserShare`/`_decreaseUserShare` → H-02/H-04/M-01; DAO finalize). Observation works.
- **Candidate birth improved** modestly: +1 new candidate (CP-1) at a locus Arm A skimmed.
- **Burden reasonable** (111 question-records, ~tens of minutes), though yield-per-question is very low
  (≈0.009 candidates/record on this contest).

Not A (0 CHECKPOINT_ONLY, 0 genuine BASE_PLUS_CHECKPOINT). Not C (there WAS candidate-birth lift + correct-
locus observation). Not D (noise did not increase materially — checkpoints emit no findings; +2 gated
candidates only).

## The central, honest finding
On unseen code the checkpoints reliably **put the question at the right place** but did **not** convert that
observation into awarded exploit chains. The accounting checkpoint fired on the exact H-02/H-04/M-01 reward
loci and the state-transition checkpoint on the M-06/M-11 vote loci — yet pre-reveal the system constructed
only a non-awarded candidate (CP-1). **The binding constraint is completing the chain (answering the question
correctly on unseen code), not observing the locus.** This is the same gap P250 flagged, now confirmed on a
state-transition-rich target: examine-time checkpoints improve *where you look*, not *whether you can finish
the reasoning once you look*.

## Implication (per spec: B → analyze the failure before building any more checkpoints)
Do **not** proceed to build the cross-contract checkpoint yet (the spec gates that on Verdict A). The failure
to analyze: checkpoints are observation aids, but recovery on unseen code is gated by chain-COMPLETION
reasoning, which a question-prompt alone does not supply. Candidate next investigations (not builds):
1. Why did answering the accounting checkpoint's questions at `_increaseUserShare` NOT yield H-02/H-04
   (first-depositor reward) pre-reveal? Is the missing step a specific invariant (empty-set branch →
   disproportionate share) the question doesn't force?
2. Measure whether *guided chain-completion* (a structured exploit-chain template per checkpoint hit), not
   just the question, closes the gap — on a held-out contest, before committing to cross-contract.
3. Coverage remains a co-bottleneck: 34/37 awards were outside the read state-core (heavily-audited salty).
