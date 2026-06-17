# P288 — VERDICT

## Verdict: **D — NO_READY_BUT_FAILURE_LOCALIZED**
## Bottleneck: **F — EVIDENCE_DERIVATION_GAP**

## Core question
Can the FROZEN stack produce another high-quality READY/PoC-supported candidate on a second fresh target before seeing
the findings? **Answer for ECG: no.** The stack surfaced and queued the right loci (incl. 2/4 exact awarded High
functions — LendingTerm.onBid H-03, SurplusGuildMinter.stake H-04) but produced **0 READY** and **0 awarded mechanism
recovery**, because no current evidence lens models ECG's awarded bug mechanisms. severe FP=0; 0 false READY.

## Why D (not A)
- A requires ≥1 exact/strong awarded mechanism recovered pre-reveal with READY/PoC support. **0 READY, 0 recovery.**
- It is D not C: C requires a READY that then fails PoC; here **no READY appeared at all**, and the funnel failure is
  localized cleanly to EVIDENCE_DERIVATION (6/8 `value_flow_present_but_no_anomaly` + NO_REFERENCE; H-03 access-refuted).
- It is not E (target was diagnostic — 29 awarded H/M, exact loci surfaced) and not F (no safety/contamination breach).

## What this tells us (the real result)
**Generalization is lens-bounded, not universal.** P287 replicated end-to-end because kelp's awarded High matched the
P284 D4.6 oracle-normalization lens. P288/ECG shows the other side: when a fresh target's awarded mechanisms
(slash-on-prior-loss, bad-debt cascade, reward-index init, share-transfer reward theft) match NO built lens, recall still
works (loci surfaced) but the evidence layer derives nothing → 0 READY. The honest two-point picture:
- **Recall + precision generalize** (right loci surfaced on both fresh targets; 0 false READY on both).
- **Mechanism derivation does NOT generalize** beyond the classes with built lenses.

## Integrity
severe concluded/reportable FP = 0 · 0 false positives · 0 fabricated passes · frozen stack unchanged (0 mismatches vs
P287 baseline) · active audit unchanged · ECG contest source unmutated · production authority WITHHELD.

## Next (decision-tree consequence)
P288 is **not** a second A → do **not** move to scaleout yet (per the stated rule). The localized next move is to repair
the **EVIDENCE_DERIVATION_GAP** with new lenses for the surfaced-but-unlifted awarded classes (priority from P288_DIAGNOSIS:
loss/slash-on-stake coupling · bad-debt/loss contagion · reward-index initialization · share-transfer reward theft), then
RE-BLIND on a third fresh target. Recall/coverage/selection/READY-gate are not the binding constraint and should not be
touched.
