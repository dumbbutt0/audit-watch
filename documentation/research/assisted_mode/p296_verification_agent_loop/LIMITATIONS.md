# P296 — LIMITATIONS

- **3 of 9 attempted this wave.** The relaxed bar (≥3 attempted / ≥1 confirmed) is met cleanly (3/3 confirmed). The
  remaining 6 allowlisted loci (kelp M-01/M-02, ecg H-01/M-02/M-03, salty H-05) are the next wave; salty H-05's
  contract is partly removed from the repo (may only reach setup_only).
- **All 3 live builders happened to be faithful** (verifier agreed), so the judge-not-the-builder override is shown
  only by the synthetic test, not by a live disagreement. A larger wave will likely surface live refutes.
- **Tier-C faithfulness, not full-contest compile.** PoCs reproduce the bug-locus control-flow with minimal mocks;
  faithfulness is argued in EVIDENCE_AUDIT (verbatim control-flow), not guaranteed by linking the real contracts.
- **Mechanism hints came from the recorded reveal/lens notes** — they steer the builder; a fully cold builder (no
  hint) might refute more. The hints are generic mechanism descriptions, not answer-key text.
- **recall-of-confirmed is cumulative-loci**, measured on the locally-answer-keyed subset; the strict-eval corpus and
  beanstalk-12 remain future waves.
