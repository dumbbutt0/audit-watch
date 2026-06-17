# P265 — VERDICT

## Decision: KEEP_SHADOW_INTEGRATE_OPERATOR_WORKFLOW  (forward build-direction: REFINE_COMPLETION_LAYER → P266)
## Trial verdict: A — SHADOW_TRIAL_PASS — **scoped strictly to the shadow recall-engine role**

### Why A (scoped) and not B
The operator's top decision branch — *noise-manageable + recall-delta-useful → KEEP_SHADOW_INTEGRATE* — is met by
the deterministic, contamination-independent metrics, and confirmed on the one clean scored anchor:
- **Noise manageable:** 16.6 advisory candidates/audit (bounded, cap=25, never floods), structured on-class
  template distribution, **0 severe concluded/reportable FP** across all 13 (guard PASS, 0 promotion flags),
  ~33% worth review, ~12 min/useful lead.
- **Recall-delta real:** **72.7%** of candidates are loci the old narrow top-5 path would skip; on the clean
  **benddao** anchor the harness forces the entire yield-staking subsystem in as recall-delta, covering **4/4
  in-class awarded Highs** (H-01/H-05/H-06/H-08) while correctly staying silent on the 4 out-of-class Highs.
- **Generalizes:** ran clean, bounded, 0-FP, recall-delta-consistent across 13 distinct architectures on the
  frozen modules (`frozen_inputs_identical_across_runs=true`; no tuning).

This is exactly the scope the operator pre-drew: *"as a shadow-mode recall engine, this is now ready to run."* The
trial confirms it.

### The hard bound — what A does NOT claim (and where a stricter reader should read B)
- **Exact-mechanism recovery is NOT validated.** benddao = **0 exact-mechanism / 1 family-level PARTIAL** (H-08,
  T5). The harness proves *locus recall*, not *mechanism recovery*. Locus recall ≠ exact recovery.
- **Completion is not run by the harness** (#4 PARTIAL/COMPLETED = 0 at harness level; the single PARTIAL is from
  P263's manual downstream run). 
- **Scored metrics are retrospective/contaminated except benddao** (n=1 clean); #3/#4/#5 are not pooled as rates.
- A reader who folds exact-mechanism into the trial bar should read this as **B — SHADOW_TRIAL_MIXED**: passes as a
  recall engine, unproven as a recovery engine. I am calling A *only* under the recall-engine scope and naming that
  threshold explicitly to avoid the over-optimism that bit P249/P251 (declared "ready," then P250/P252 showed 0 lift).

### No production authority
Per the standing rule and the operator's own line, the harness stays **default-off, shadow, advisory, un-wired**.
Nothing here grants routing/severity/submission/dashboard authority. "0 concluded/reportable FP" is by construction,
not measured precision.

### Required next step — P266
**Exact-mechanism recovery, proven repeatedly on fresh public-findings contests**, before any production-authority
consideration. The bottleneck is now unambiguous and consistent across the whole arc: the **recall/discovery layer
works; the completion / exact-mechanism layer is the open gap** (REFINE_COMPLETION_LAYER). P266 should run the B/C
ranking + five-op completion on the recall-delta loci this trial surfaces, on ≥2 clean fresh contests, and score
exact-mechanism recovery — not locus recall.

### Constraints honored
No build / tuning / promotion / wiring. Harness + P260 + P262 + configs byte-identical (verified pre/post).
Forbidden files byte-identical. Active audit `size-credit-2024-06-blind` unchanged. Guard PASS + 0 promotion flags
on all 13. Reveal records used only for retrospective scoring, never to generate candidates.
