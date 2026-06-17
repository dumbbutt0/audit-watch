# P298 — LIMITATIONS

- **Not a fresh blind run.** Evals the pre-existing 44 findings; recall (34/81) is the prior eval2 number, re-surfaced
  read-only. P298's NEW contribution is the novelty + executed-validity axes, not new discovery.
- **The answer-key match is a prior semantic judge** (eval2), not re-judged here. P298 reports it; it does not
  re-derive HIT/PARTIAL/MISS.
- **The verifier is exploit-shaped.** Its L1 (attacker EOA) + L2 (named state flip) contract under-credits
  logic/correctness/admin bugs (LG-001/PC-001/SN-001 scored setup_only despite passing differential tests on verbatim
  source). This is the FP-guard erring safe, and the clear next improvement: a logic-bug validity mode (validity = a
  passing differential test vs a corrected reference; no attacker L1 required).
- **Tier-C, batch.** 5 of 12 accepted got executed PoCs; 7 are evidence-bundles (needs_execution) because faithfully
  mocking the full reseed/migration/AMM systems is infeasible Tier-C. Those bundles are the next validity wave.
- **Novelty is local-KB-cosine + spot immunefi.** 0/44 novel at 0.4 is honest (all map to known classes) but a
  threshold/embedder choice; immunefi crossref was run on the 2 confirmed loci, not all 44.
