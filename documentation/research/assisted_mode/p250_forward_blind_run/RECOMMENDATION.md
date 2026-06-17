# P250 — Recommendation / Verdict

## Verdict (exactly one)

# B — PARTIAL_GENERALIZATION

On a genuinely unseen target the accounting checkpoint **generalized architecturally** — it fired only on
real accounting loci (reinforcing every base accounting candidate at the correct function), emitted **0
findings / 0 conclusions / 0 false positives**, cost **0.066 s** + a bounded **29** question-records, and did
not behave like a detector. But it produced **0 recall lift**, because spectra's two awarded findings are
**not accounting-family** (M-01 = permission/ERC-5095 compliance; M-02 = cross-contract flashLoan
vault-deflation). So *generalization of the architecture* is confirmed; *recall lift from the accounting
checkpoint specifically* was not demonstrated on this contest.

### Why not A (CONFIRMED_GENERALIZES)
A would require a demonstrated recall lift on the unseen target. There was none — not because the checkpoint
failed, but because this contest had no accounting-family awarded finding to recover. Honesty (no optimism):
the value was not shown here, only the FP-safety and correct-firing.

### Why not C (DOES_NOT_GENERALIZE)
C would require the checkpoint to misbehave (emit findings, set severity, flood with FPs, or fail to fire on
real accounting code). The opposite happened: it fired precisely on the real accounting surface, stayed
silent on the out-of-domain permission bug (M-01), reinforced the cross-contract locus (M-02), and added 0
FP. The architecture works.

## What this tells us (consistent with P247/P248)
- The accounting checkpoint is **FP-safe and cheap on unseen code** — the P249 architecture claim holds out
  of sample.
- But accounting was always the *lowest-recovery* checkpoint (P248: chosen FIRST for FP-tight architecture
  validation, not for recall). Spectra's bugs land squarely in the **two higher-value families that are not
  yet built**: cross-contract (M-02) and permission (M-01, sibling of state/permission). This is direct,
  unseen-target evidence that the remaining recall lives there.

## Recommendation (next steps — separately approved)
1. **Build the state-transition checkpoint next** (P248's highest-absolute-recovery #2) using the validated
   accounting template — it carries the reasoning Highs.
2. **Then the cross-contract checkpoint** — it would have addressed spectra's M-02 (and decent's cross-chain
   misses). A permission checkpoint would address M-01-class compliance/auth bugs.
3. **Re-run a forward-blind on an accounting-bug-bearing unseen contest** to demonstrate accounting lift
   specifically (spectra simply had none) — optional, since the architecture is already validated.

## Honest limits
- n = 1 unseen contest; the 0-lift is one data point driven by contest bug-mix, not a population estimate.
- Training-confound: spectra is public → the base 25% is an upper bound; the checkpoint-attributable delta (0)
  is the confound-light result.
- No PoCs (BLOCKED_BY_BUILD), so even the base PARTIAL on M-02 is unproven.
