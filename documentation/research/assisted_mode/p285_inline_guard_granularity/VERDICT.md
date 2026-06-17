# P285 — VERDICT

## Verdict: **A — D1_GRANULARITY_READY_FOR_POC_SWEEP**

## Core question
Can D1 distinguish "read used in value/recipient computation" from "guard that gates execution", unblocking valid
relationship-error candidates without reintroducing false READYs or missing true guards? **Answer: yes.** D1 now refutes
only on execution-gate constructs; `claim_many` (Blackhole M-04) is no longer falsely D1-refuted and lifts to READY,
while every true guard remains refuted and severe FP stays 0.

## Scorecard vs the A-bar
| criterion | result |
|---|---|
| true inline guards remain refuted | ✔ (41 EXECUTION_GUARD; V3Vault.transform + VotingEscrow.withdraw refuted) |
| claim_many no longer falsely D1-refuted | ✔ (ownerOf → RECIPIENT_READ) |
| ≥1 relationship-error candidate becomes READY (or correctly blocked for a non-D1 reason) | ✔ (claim_many → READY) |
| no P281–P284 false-READY regressions | ✔ (only claim_many newly READY; 116 prior tests green) |
| L2Governor.execute remains READY/PASS_SUPPORTED | ✔ (PoC 2/2) |
| V3Vault.transform remains not READY | ✔ (real if-revert) |
| IBeanstalk declaration-only remains not READY | ✔ (NEEDS_SOURCE_SPAN) |
| audit finds no hallucinated source context | ✔ |
| severe concluded/reportable FP = 0 | ✔ |
| no production-authority leakage | ✔ (advisory stamps; reused/P283/P284 byte-identical) |
| tests green | ✔ (P285 + P260–P284) |

## Net effect of P285
- **First awarded relationship-error bug carried to READY** by the assisted-mode chain: `claim_many` (M-04), via P282
  anomaly + P284 SIBLING_REFERENCE_FOUND, finally unblocked by the corrected D1.
- **D1 precision sharpened both ways:** token-in-execution-gate (require/assert/if-revert/modifier/custom-error) keeps
  true guards refuting (INLINE_GUARD_REFUTED 36→29 reflects only false read-blocks removed), while ownership/value
  READs no longer suppress recipient/rewards/sibling bugs. New fail-closed `NEEDS_GUARD_CONTEXT` for ambiguous auth.
- **A true-guard gap was found and fixed during the audit** (`assert()` was not covered → VotingEscrow.withdraw; added
  `assert` to gate detection → correctly refuted again). This is exactly the FP-safety the phase was meant to protect.

## Production authority
**WITHHELD.** Research-only, advisory, un-wired, default-off, fail-closed.

## Next
Small PoC sweep on the now-trustworthy READY set (claim_many L3 recipient-flip + L2Governor) → fresh blind target. Then
the P284 backlog (share-math corrected-reference helper / cross_contract_sibling_parity) for more relationship-error
breadth.
