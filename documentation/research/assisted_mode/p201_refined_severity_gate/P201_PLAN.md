# P201 — refined severity-gate design + second fresh-corpus validation

## Goal
Refine the P199/P200 severity discriminator to fix P200's out-of-sample failures, then validate it on a **second
fresh sealed corpus** (zetachain-2023-10, 14H/34M). Design + out-of-sample validation **only** — no production wiring.

## What P200 told us (the refinements to make)
- Griefing/DoS→Medium **generalized** → keep.
- Oracle→High and precision→High **did not generalize** (predy M-04/M-03 awarded Medium, kept High) → make
  **evidence-conditional / magnitude-dependent**.
- Per-**surface** grading folded a real secondary High (H-02) under a Medium primary (M-06) → grade
  **per mechanism**, preserve secondary Highs.

## Standing caveat (user-directed)
Oracle severity is **UNVALIDATED_OUT_OF_SAMPLE** — no fresh sealed corpus has oracle surfaces. The oracle branch is
**design-only**; P201 must not claim it production-validated. Oracle re-test is deferred to **P202** (oracle-rich
corpus search) → **P203** (oracle gate validation). P201 tests precision · DoS/griefing · auth · theft · per-
mechanism + secondary-High preservation.

## Out-of-sample property (double freeze)
1. FREEZE 1 — blind threat-ceiling verdicts (Sonnet on production `deep_trace.md ef93a6c2` + verbatim source).
2. FREEZE 2 — refined **mechanism-level** gate applied offline, answer-key-blind, frozen as harness constants.
3. Then open the seal and score original-vs-refined, **per mechanism**.

## Sequence
Integrity precheck → P200 failure extraction → refined 6-class gate design → zetachain count-only viability →
blind ~18-surface campaign (FREEZE 1) → offline refined gate (FREEZE 2) → controlled per-mechanism scoring →
deliverables → decision.

## Decision space
`REFINED_GATE_VALIDATED` · `REFINED_GATE_PARTIAL` · `REFINED_GATE_FAILED_FALSE_DEMOTIONS` ·
`ORACLE_PRECISION_FRONTIER_UNRESOLVED` · `DATASET_TOO_THIN` · `INVALID_RUN` — qualified "(non-oracle)"; oracle
carried as UNVALIDATED_OUT_OF_SAMPLE regardless.

## Guardrails
Read-only/offline; production hashes byte-identical START==END; gate offline-only (never implemented); double
freeze recorded; mechanism-level scoring with secondary-High preservation; blind firewall (prompts+outputs leak-
scan, scorer post-freeze); Sonnet; `fabrication_rate=0`; bounded sample = out-of-sample signal not full recall.
