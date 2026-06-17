# P286 — VERDICT

## Verdict: **A — READY_SET_POC_SUPPORTED**

## Core question
Does the `claim_many` READY convert into a PoC-supported finding — is the claim↔claim_many recipient divergence real and
runtime-provable (L1/L2/L3)? **Answer: yes.** All three tests pass; the divergence is the omitted AVM `getOriginalOwner`
correction; L2Governor remains PASS_SUPPORTED.

## Scorecard vs the A-bar
| criterion | result |
|---|---|
| claim_many divergence proven (all 3 tests pass) | ✔ (3 passed / 0 failed) |
| L1 entry permissionless · L2 named state-flip · L3 outcome | ✔ all three layers |
| L2Governor.execute still PASS_SUPPORTED | ✔ (2 passed) |
| faithful reproduction (verbatim control-flow), no fabricated pass | ✔ (audit clean) |
| severe concluded/reportable FP = 0 | ✔ |
| no production-authority leakage | ✔ (advisory; frozen/forbidden byte-identical) |
| tests green | ✔ (P286 + P260–P285) |

## The milestone
The assisted-mode chain has now crossed the full path end-to-end for an awarded relationship-error bug:
**surface → route → relationship/invariant evidence (P284 SIBLING_REFERENCE_FOUND) → avoid false D1 suppression (P285)
→ READY_FOR_POC_INTENT → PoC-supported (P286).** That was not possible before this arc. The READY set converts:
2/2 PoC-supported (claim_many newly proven; L2Governor confirmed).

## Production authority
**WITHHELD.** Research-only, advisory, default-off; Tier-C faithful reproduction (not a submission package).

## Next
Per the user: go to a **fresh blind target** to check generalization of the stacked P274–P285 supervised improvements,
before any further repair. The supervised pipeline now behaves as a reliable factory for a small number of very
high-quality PoC targets; the open question is whether that holds blind.
