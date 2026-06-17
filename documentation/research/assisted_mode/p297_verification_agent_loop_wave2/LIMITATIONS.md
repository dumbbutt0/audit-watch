# P297 — LIMITATIONS

- **Execution-confirmed ≠ awarded-mechanism-confirmed.** The verifier proves a PoC runs and asserts what its manifest
  claims; it does not prove the PoC's mechanism is the EXACT awarded mechanism. 2/9 (ecg M-02, kelp M-01) are
  fidelity-caveated and routed to human review; the other 7 are high-fidelity (verbatim control-flow + clear defect).
- **9/9 verifier-confirmed is the TRACTABLE batch** (exact-function loci, recorded mechanisms, local source). The
  harder beanstalk-12 (prose, large L2-migration codebase) will likely have refutes/setup_only — not yet attempted.
- **Tier-C faithfulness**, not full-contest compile; faithfulness argued per-locus in EVIDENCE_AUDIT (verbatim
  control-flow), not guaranteed by linking the real contracts. Some PoCs model an integration boundary (kelp M-01
  EigenLayer window; salty H-05 partly-removed contract — its cooldown path was reconstructed from source).
- **Builders were given mechanism hints** (from the recorded reveal/lens notes) — they steer fidelity; a fully cold
  builder would likely refute more. Hints are generic mechanism descriptions, not answer-key text.
- **recall-of-confirmed = confirmed awarded LOCI by execution** on the locally-answer-keyed subset; the strict-eval
  corpus + beanstalk-12 remain future waves; submission authority stays withheld.
