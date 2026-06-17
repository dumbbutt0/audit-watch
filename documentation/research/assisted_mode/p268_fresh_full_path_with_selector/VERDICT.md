# P268 — VERDICT

## Bottleneck: TRIAGE (candidate-selection-for-PoC)
## Verdict: B — SELECTOR_HELPFUL_NEEDS_MORE_PROOF

### Why
On a fresh, zero-exposure external contest (karak), with the P267 selector inserted between B/C ranking and
completion/PoC:
- **The P267 selector worked and fixed the P266 drop — on fresh data.** It returned KEEP_BOTH on both real pairs
  (anti-easy-PoC flag set), preserving the high-impact mechanisms (C1-M1 finishRedeem-accounting, C2-M1 inflation)
  that the raw pre-P267 path would have dropped for the easy rivals (approval-revert, dust-rounding). The preserved
  C2-M1 was carried to completion + PoC and **confirmed a real victim loss** (first-depositor inflation: a 5000e18
  deposit → 0 shares). The selector also correctly REFUTE_FIRST'd the gated slashing control. The specific
  RANKING_GAP failure from P266 **did not recur**.
- **BUT exact awarded recovery = 0.** Two honest reasons: (1) the PoC-confirmed mechanism (Vault first-depositor
  inflation) is **real but not awarded** (the report states no distinct first-depositor/decimalsOffset finding was
  awarded); (2) all 9 awards cluster in the **NativeVault/slashing/snapshot** subsystem, which the recall harness
  **surfaced** but **triage de-scoped** (pre-reveal, for PoC-feasibility — "needs beacon fixtures"). The selector can
  only choose among mechanisms triage routes to it.

So the selector is **demonstrably helpful** (it did exactly what P267 promised, now confirmed on fresh data with a
real PoC), but the full path did **not** produce an exact/strong awarded recovery this round → **B, needs more proof**.

### Why not A
A requires ≥1 EXACT_AWARDED_MECHANISM or ≥2 STRONG_MECHANISM_MATCH with a PoC-supported recovery. Result: 0 exact,
0 strong (awarded). The confirmed mechanism was not awarded. No hindsight credit taken.

### Why not C / D / E / G
- Not **C** (PRESERVED_BUT_COMPLETION_FAILED): completion did **not** fail — C2-M1 completed and was PoC-confirmed.
  The miss is not-awarded + a triage de-scope, not a completion failure.
- Not **D** (SELECTOR_FAILED_RANKING_STILL_BLOCKS): the selector did **not** fail — it preserved the high-impact
  mechanism; ranking no longer blocks.
- Not **E** (POC_LAYER_BLOCKED): the PoC layer produced a clean L3 confirming PoC.
- Not **G** (ABORTED): no safety/contamination trigger — 0 severe concluded/reportable FP, no award leak before the
  Phase-11 freeze, frozen modules + 5 forbidden byte-identical, active audit unchanged, contest source unmutated.

### The bottleneck moved upstream (the real finding)
P266 = RANKING_GAP → P267 fixed it → **P268 shows the binding constraint is now TRIAGE**: the award-dense subsystem
was surfaced by recall but not routed into the expensive PoC path (de-scoped on PoC-feasibility). This is the P259
"selection-upstream" theme recurring at the triage stage. No regression; the gap is newly-localized.

### Required next step — P269
Address the **TRIAGE gap**: route candidate selection by award-class-fit / impact (don't de-scope a recall-surfaced
high-value subsystem just because it needs a heavier PoC harness); ensure the slashing/snapshot-style subsystems the
recall layer surfaces are carried into completion. Then re-run the full path (P260→…→P267→completion→PoC) on ≥1 fresh
contest and score exact recovery. Production authority remains **withheld**.

### Constraints honored
No production authority / auto-submission / severity / reportable / submission-ready. Frozen modules byte-identical
(verified pre/post): P260 `d6b494bc` · P262 `a48336275f` · P264 `85f9cbe6` · **P267 `b0623b8c`** (+ configs). 5
forbidden byte-identical. Active audit `size-credit-2024-06-blind` unchanged. Karak source isolated in `/tmp`
(never under `audits/`); contest source unmutated; PoCs under `pocs/p268/`. Answer key opened only after the full
pre-reveal freeze manifest was hashed. No answer-key content used to generate candidates or assign selector dimensions.
