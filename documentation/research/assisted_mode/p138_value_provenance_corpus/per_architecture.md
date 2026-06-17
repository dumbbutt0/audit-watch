# P138 — Per-Architecture Breakdown

| arch | buggy useful-recall | buggy strict | clean FP | items |
|---|---|---|---|---|
| noya | 2/3 (B1 HIT, B2 HIT; B3 MISS) | 2/3 | 0/2 (C2,C4 clear) | B1,B2,B3,C2,C4 |
| size-credit | 1/1 (B4 PARTIAL) | 0/1 | 0/1 (C5 clear) | B4,C5 |
| blackhole | 1/1 (B5 HIT, aided) | 1/1 | 0/2 (C1 HIGH, C3 clear) | B5,C1,C3 |
| **total** | **4/5 useful (80%)** | **3/5 (60%)** | **0/5 FP** | 10 |

Generalization: useful detection on ≥3 architectures; zero clean FP on all 3. The MISS (noya H-13) and the
needs_human (size M-02) are the harder subtle/spec-dependent cases. blackhole HIT is context-aided.
