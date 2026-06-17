# Phase 79 — A/B/C Workflow Eval: does verification hygiene improve audit decisions?

**Result: PASS (safety).** On a frozen 15-candidate batch, the full workflow (arm C = defense-first + P78 hygiene +
adversarial review) is the **only** arm with **0 unsafe promotions** (0 unsupported READY · 0 SOURCE_FALSE · 0 OVERFIT ·
0 WRONG_MECHANISM · 0 HARD_FAIL), versus **9 unsafe for baseline (A)** and **5 for defense-first (B)**. This is a
**deterministic workflow-discipline eval — NOT proof of autonomous hit discovery and NOT a live-agent run.**

## Honesty caveats (read first)
- This eval is a **deterministic simulation of workflow discipline**: the three arms differ only in *which evidence each
  workflow consults*, and a **post-hoc scorer** compares each arm's output to a **held-out `ground_truth`**. It demonstrates
  that the hygiene layer changes decisions, not that an autonomous agent discovers bugs.
- **Hit-accrual is NOT proven.** The one genuine clean lead (`FRESH-synthetic-missingnonce`) is promoted by **all three
  arms** — C does not *uniquely* accrue hits; it preserves genuine leads while killing false promotions. Positive anchors
  are excluded from hit-accrual by design.
- **Live-agent readiness: NOT demonstrated.** Live A/B/C with real LLM investigation is future work.

## Approach + profile fairness (exactly what evidence each arm receives, and why)
All three arms run the same P77 `deep_pass` state machine; they differ only in the evidence each consults — the faithful
difference between the workflows. Arms are **blind to ground_truth** (the projected view strips it; arms assert its absence;
`test_1` proves arms are ground-truth-invariant; `test_2` proves they reject a non-projected dict).

| arm | context | exploit | defense ledger | source-falsification | adversarial + hygiene | models |
|---|---|---|---|---|---|---|
| **A baseline** | yes | yes (baseline-plausible, possibly wrong mechanism) | **none** | **none (all-false)** | **no** | confident agent, weak defensive tracing |
| **B defense-first** | yes | yes | **full (reject-first)** | **none (all-false)** | **no** | defense mapping, no falsification/review |
| **C full** | yes | yes | full | **real** | **yes (hygiene_validate fail-closed + adversarial)** | the P77+P78 workflow |

(Every candidate's exploit carries a non-empty `rejection_case` — a baseline writes *some* shallow reasoning — so the
deep_pass reject-first *presence* gate does not unfairly stop arm A; A still over-promotes because it lacks the defense
ledger + falsification.)

## Batch composition (`_p79/candidate_batch.json`, 15)
3 positive anchors · 3 negative controls · 3 wrong-mechanism traps · 3 defense-present traps · **3 fresh/semi-fresh leads**
(LooksRare `execute` & Astaria `buyoutLien` = semi-fresh real subjects **not** used in P77/P78 bundles; one synthetic fresh
missing-nonce lead). Grounded in prior-phase reality (AI Arena state-bound hash, DYAD/Olas/reNFT by-design,
multicall final-invariant, permit nonce-consumed, …). `ground_truth` held out.

## Result table (category counts; 15 each)
| arm | CLEAN_HIT | STRONG_PARTIAL | REJECT_CORRECT | ABSTAIN_CORRECT | WRONG_MECHANISM | SOURCE_FALSE | OVERFIT | HARD_FAIL |
|---|---|---|---|---|---|---|---|---|
| A baseline | 1 | 3 | 0 | 2 | **3** | **1** | **5** | 0 |
| B defense-first | 1 | 3 | 3 | 3 | **3** | **1** | **1** | 0 |
| **C full** | 1 | 2 | **8** | 4 | **0** | **0** | **0** | 0 |

## Separated scoring (per the discipline)
**1. Safety improvement** (unsafe = unsupported_ready + source_false + overfit + wrong_mechanism + hard_fail):
A = **9** → B = **5** → C = **0**. C is the only arm that promotes nothing it should reject.
**2. Mechanism correctness** (WRONG_MECHANISM): A = 3 → B = 3 → C = **0**. Defense-first alone does NOT fix wrong-mechanism;
source-falsification + adversarial review (C) does.
**3. Hit-accrual evidence:** **NOT proven.** The genuine fresh lead is hit by all arms; C uniquely accrues nothing.
**4. Live-agent readiness:** **NOT demonstrated** (deterministic simulation).

## What C does / does not do (honest)
- C **rejects every trap** (defense-present, wrong-mechanism, source-falsified) with a source-backed reason, and recovers
  the genuine bugs (1 CLEAN_HIT + 2 STRONG_PARTIAL) with 0 false-positive promotion.
- C **safely abstained** on one under-specified anchor (`ANCHOR-vf-computed-unapplied`) because its defense ledger did not
  classify the critical `final_invariant_check` → hygiene correctly demanded it (`NEEDS_CONTEXT`). This is the discipline
  working (a safe abstain), not a false promotion — and is why C's STRONG_PARTIAL (2) is one below A's (3). C trades a
  little recall for safety.

## Pass / fail
**PASS (safety):** C has 0 unsupported READY · 0 SOURCE_FALSE · 0 detector→finding · 0 HARD_FAIL · WRONG_MECHANISM (0) <
A (3) · all C REJECTs source-backed · safety strictly improves A → B → C. **Stretch (hit-accrual): NOT met** (no unique
fresh hit by C) — correctly reported as safety-only per the constraint "if all C does is reject traps and recover anchors,
report PASS for safety only."

## Integrity
`scripts/investigation/abc_eval.py` (`5e0d855d`) + `_p79/candidate_batch.json` + `_p79/abc_results.json` + this report +
`tests/investigation/test_abc_eval.py` (9). P77/P78 modules byte-identical (deep_pass `57c29fff`, lead_schema `3c57f04e`,
transitions `2c00069c`, hygiene_validate `b9e18f29`); parked detectors (`f9ec0bff`/`2337edc2`/`e72b9994`) + value-flow
(`697e72a7`/`5522e15f`/`aca9125a`) byte-identical. Full regression **123 passed** (investigation 28 + signature_replay 22
+ access_control 51 + candidates 22). No-wiring CLEAN. No new detector logic; no production wiring; arms blind to ground
truth. **Promotes nothing to production.**

## Recommended next
Safety is proven; hit-accrual + live-agent readiness are not. **P80 — live-agent A/B/C (small, manual-approval):** run a
few held-out leads through the *actual* skills (`/audit-candidate-verification` + `/adversarial-bundle-review`) in-session
and score by the same 8 categories, to test whether the discipline survives live reasoning (the bridge to real bounty
performance). Alternatively **P80 — PoC handoff gate** (only concrete-attacker-sequence candidates enter the PoC builder).
North star: high recall at the lead layer, near-zero false-positive promotion at the review layer.

## Reproduce
```
python3 scripts/investigation/abc_eval.py --self-test
python3 scripts/investigation/abc_eval.py --run --out documentation/research/_p79/abc_results.json
~/.local/bin/pytest tests/investigation/ -q                                  # 28 passed
~/.local/bin/pytest tests/signature_replay/ tests/access_control/ tests/candidates/ -q
```
