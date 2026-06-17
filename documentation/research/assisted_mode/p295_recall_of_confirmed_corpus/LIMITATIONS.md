# P295 — LIMITATIONS

- **Sealed strict-eval excluded.** The ~183-awarded strict-eval corpus has sealed answer keys → recall-of-confirmed
  can't be measured there locally (only externally). This phase measures the locally-answer-keyed subset.
- **beanstalk is finding-level.** Its awarded loci are prose titles (no clean contract.fn), and `surfaced` is taken
  from `accepted` (system finding matched). It contributes to the denominator but has no PoCs yet (all backlog).
- **blackhole is partial_local.** No reveal artifact → only the two loci with local evidence (claim_many, L2Governor)
  are counted, as additional confirmed (not in the full-local recall denominator). Its full awarded set is external.
- **Tier-C faithfulness.** The PoCs reproduce bug-locus control-flow with minimal mocks (the validated pattern); they
  are not compiled against full contest source. Faithfulness is argued in EVIDENCE_AUDIT.
- **Climb is one new PoC.** recall-of-confirmed moved from 2 (P294) to 6 loci, but the full climb to ~100% needs the
  verification-agent loop to build PoCs for the 21-item surfaced backlog — that is the next phase, not this one.
- **recall_of_surfaced uses recorded reveal status**, not a fresh open-recall re-run; it reflects the surfacing the
  arc phases recorded. A fresh ungated re-run could differ.
