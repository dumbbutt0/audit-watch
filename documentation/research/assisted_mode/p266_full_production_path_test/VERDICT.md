# P266 — VERDICT

## Bottleneck: C — RANKING_GAP
## Verdict: C — POC_LAYER_READY_RANKING_NEEDS_REFINEMENT

### Why
The first full production-path run (phi-2024-08, scored, freeze-before-reveal) proved the **infrastructure** but not
**exact mechanism recovery**:
- **Dashboard route works, advisory-only:** standalone feed + page; every record `ADVISORY_RECALL_CANDIDATE`,
  severity null, 0 promotion flags; no promote/confirm/submit control; no touch of `dashboard.py`/`dashboard_sync.py`/
  canonical records.
- **PoC layer works:** 3 runnable foundry PoCs built from advisory candidates with full L1/L2/L3 evidence; the
  negative control (`withdrawWithSig`) was correctly benign and confirmed benign at reveal.
- **0 severe concluded/reportable FP**; reportability gate appropriately conservative; active audit unchanged.
- **BUT exact mechanism recovery = 0 exact / 0 strong.** The path surfaced the **exact awarded locus**
  (`CuratorRewardsDistributor.distribute` = awarded **H-03**) and **enumerated the awarded mechanism family**
  (curator-enumeration gas-DoS, m1c, into Profile-B top-2) — then **mis-ranked it below a non-awarded mechanism**
  (royalty→caller) and PoC'd the wrong target. The two PoC'd mechanisms were SAME_AREA_WRONG_MECHANISM.

### Why not A
A requires (≥1 EXACT_AWARDED_MECHANISM **or** ≥2 STRONG_MECHANISM_MATCH) with ≥1 PoC-supported recovery. Result is
**0 exact, 0 strong**. The awarded mechanism was *discovered and enumerated* but not *selected/recovered*. A would
repeat the P249/P251 over-optimism the arc has been correcting.

### Why not G (abort)
No safety/contamination trigger fired: no candidate ever acquired a concluded/reportable/severity field; no answer
content leaked before the Phase-8 freeze; forbidden files byte-identical; active audit unchanged. Safety held fully.

### Why C and not B or D
- Not **B** (DASHBOARD_ROUTE_READY_POC_LAYER_NEEDS_REFINEMENT): the PoC layer is *not* the weak link — it produced
  3 passing L3 PoCs and a correct negative control. The PoCs were simply aimed at the wrong mechanism.
- Not **D** (RECALL_ENGINE_READY_BUT_FULL_PATH_NOT_READY): too vague — it understates that dashboard + PoC + gate
  all worked. The single, specific, reproducible gap is ranking/selection.
- **C** is the precise call: the dashboard and PoC layers are ready; **ranking/selection refinement** is the
  blocking work, exactly as the bottleneck (RANKING_GAP) shows. This matches the P256/P257 finding (when the
  awarded mechanism is enumerated, the failure is ranking) — now reproduced through the full production path.

### Mechanism precision vs P263/P265
**No improvement.** P263 = family-level PARTIAL / 0 exact; P265 = 0 exact across the corpus; P266 = 0 exact / 0
strong, with the awarded mechanism generated-but-misranked. Locus recall keeps working; exact mechanism recovery
remains unproven and is now pinned to ranking/selection.

### Required next step — P267
Refine **ranking + selection** so an enumerated awarded mechanism is chosen #1 for completion/PoC over an
easier-to-PoC non-awarded one. Concretely: weight impact/awarded-class fit (a permanent reward-distribution **DoS**
> a 1% royalty skim) above PoC-feasibility in selection; force the Profile-B/C top-2 to BOTH be carried into
completion (not just #1). Re-run the full production path and score **exact mechanism recovery** on ≥2 fresh
public-findings contests before any production-authority consideration. Production authority remains **withheld**.

### Constraints honored
No auto-submission; no severity/routing/submission/confirmation-gate/min-confirm/canonical-schema/detector/
checkpoint/run_pipeline edits; no production or contest source edits (phi `src` copied read-only into the isolated
PoC project; libs cloned at pinned versions). Frozen modules + 5 forbidden files byte-identical (verified pre/post).
Active audit `size-credit-2024-06-blind` unchanged. Answer key opened only after the Phase-8 freeze manifest was
hashed.
