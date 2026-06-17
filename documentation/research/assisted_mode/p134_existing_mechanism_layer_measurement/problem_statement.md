# P134 — Problem Statement

P133 graded the noya boost-delta and found the **surface specialist** caught HIT 2 / PARTIAL 3 / MISS 3
(useful 5/8). The remaining gap was framed as needing a "deep-pass mechanism layer." But exploration found
mechanism-depth detectors for these exact classes **already exist** in the repo. So before building anything,
P134 **measures whether the existing mechanism layer recovers the P133 visible-but-MISS/PARTIAL classes** and
isolates the *true* residual.

**Primary question:** Do the existing mechanism-depth detectors close the P133 depth gap?

**Discipline (separate concerns):** visibility (P130-132) ≠ detector-flag ≠ mechanism-correctness ≠
exploitability ≠ submission-readiness. A detector that flags the right function but the wrong/incomplete
mechanism is **PARTIAL, not HIT**. Advisory/report-only/research-only output is **not** submission-ready.

**Target set:** the 8 noya boost-delta awarded functions with their P133 labels (HIT/PARTIAL/MISS); non-awarded
boosted functions are a noise/control sample only. The answer key is used **only** to score, never to tune.

**Constraint:** no new detector unless measurement proves the existing layer cannot cover a residual class.
