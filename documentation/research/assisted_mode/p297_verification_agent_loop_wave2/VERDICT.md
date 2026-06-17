# P297 — VERDICT

## A — WAVE2_CONFIRMS_ALL_TRACTABLE_LOCI_AT_FP_ZERO

The loop spawned builders for the remaining 6 loci; the verifier (sole judge) confirmed all of them, and cumulative
recall-of-confirmed climbed to 15 loci at confirmed-FP = 0.

### A-criteria — all met
- **All 6 wave-2 loci attempted** (PoC produced + judged), via spawned subagents; all 9 tractable loci now judged.
- **Verifier confirmed all 6** (cumulative 9 across waves 1+2): ecg H-01/M-02/M-03, kelp M-01/M-02, salty H-05 —
  each a real forge exploit PASS (L1+L2+L3) with an assertion_map.
- **Cumulative recall-of-confirmed: 6 → 15 loci.**
- **confirmed-FP = 0** — verifier is the sole confirmer; builder claims advisory; refutation control stays refuted;
  no confirmed_but_unmapped.
- **Honest fidelity grading:** 9 verifier-confirmed = **7 high-fidelity + 2 fidelity-caveated** (ecg M-02 possible
  by-design rate-limit; kelp M-01 EigenLayer-window assumption) → routed to human review. The locus recall is real;
  the exact awarded mechanism on the 2 caveated awaits human confirmation.
- Funnel + re-ranked backlog updated; P296 wave-1 snapshot preserved; new files only (loop edit additive, unpinned).

### What this validates
The verification-agent loop scales: spawn builders at the surfaced backlog, let the verifier judge. The new property
this wave surfaced — **execution-confirmation is not the same as awarded-mechanism fidelity** — is handled honestly by
the assertion_map + a human-review tier for the 2 caveated, without any false confirmation (FP=0).

### Next
beanstalk-12 wave (expect refutes/setup_only on the prose findings); strict-eval once answer keys are available; a
surfacing pass for the 4 missed; human review of the 2 fidelity-caveated; re-blind once recall-of-confirmed holds at
confirmed-FP=0. Submission stays human-gated.
