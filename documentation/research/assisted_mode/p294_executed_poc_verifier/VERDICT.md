# P294 — VERDICT

## A — EXECUTED_POC_ORACLE_PROVEN (recall opens; FP≈0 by proof)

The executed-PoC verifier confirms awarded loci by ACTUAL forge execution, refuses a false hypothesis, and never
confirms without a real passing exploit run.

### A-criteria — all met
- **≥1 awarded locus confirmed by a real forge execution:** TWO —
  - `blackhole claim_many` (awarded M-04) → `confirmed_by_execution`, `attacker_verified=True`, L1+L2+L3.
  - `salty _increaseUserShare` (P293-recovered) → a **net-new Tier-C PoC built + executed this phase** →
    `confirmed_by_execution` (the full open-recall→verify loop on a freshly recovered locus).
- **≥1 false-hypothesis candidate correctly not confirmed:** `salty Pools.deposit` → `refuted_by_execution`,
  `attacker_verified=False` (only the refutation test passes).
- **confirmed-FP = 0** — every confirmation is an awarded locus backed by a real passing exploit run + log.
- **Open-recall flow demonstrated** via the proof driver over a candidate list (no edit to existing modules).
- **No auto-submission path** — verifier sets no severity/submission_ready; un-wired from confirm_gate/min_confirm_gate
  (asserted). The anti-fabrication + setup_only guards both hold (synthetic tests).

### What this buys
Precision is now bought by PROOF, not by blocking. That removes the lens-bound on recall: candidates can flow wide
and the executed PoC is the FP oracle. confirmed-FP stays ≈0 by construction, and unlike a pattern gate it
generalizes.

### Next
A → (i) corpus-wide open-recall + demote the fail-closed gates to advisory, measuring recall-of-confirmed toward
~100% on the dataset; (ii) the verification-agent loop (auto-build PoCs per surfaced candidate); (iii) re-blind only
after confirmed-FP holds. Submission authority stays withheld until the verifier feeds the existing confirm gates
with a human in the loop.
