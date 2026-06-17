# P102 — Blind autonomous invariant-validation replay

**Subject:** code4rena **IQ AI 2025-01** @ `db0d369b` (7 in-scope contracts, 1479 lines) — fresh/unseen; not
M-11; not a P101 regression subject. **Sealed-key discipline:** ranking + `prekey_freeze.json`
(`answer_key_opened:false`) frozen *before* the Code4rena report was opened.
**Verdict: PARTIAL PASS** (recall+precision objectives met for the top migration finding; validation depth
capability-bound, as predicted).

## Primary question
*Can the system autonomously generate the correct invariant among many candidates and let the precision gates
elevate it without human intervention?* → **YES for the top migration finding (M-01):** among 224 generated
candidates, the system autonomously produced the relevant invariant on `LiquidityManager.moveLiquidity` and the
precision pipeline surfaced it as the **#1 human-actionable** candidate **with no human invariant selection and
zero false promotions** — while honestly holding it at `NEEDS_EXECUTION` (a migration manipulation needs a fork
PoC). Elevation to a CONFIRMED finding still requires the human/fork step.

## Pre-key blind prediction (frozen)
`LiquidityManager.moveLiquidity` `ordering_race`/`cross_contract` → `NEEDS_EXECUTION`: *permissionless migration
seeds Fraxswap at a manipulable price; an attacker can pre-create the pair / sandwich the 3-round alignment
swaps.* `validated_for_poc = 0` (no confident VALIDATED blind).

## Answer key (opened only after freeze): 1 High + 3 Medium
- **H-01** `TokenGovernor` quorum numerator `4` vs `25` (constructor).
- **M-01** `moveLiquidity`/`addLiquidityToFraxswap`: anyone can pre-deploy the Fraxswap pair with a low fee → loss.
- **M-02** `moveLiquidity`: migration amount uses raw `currencyToken.balanceOf` → injectable → DoS.
- **M-03** `setProposalThresholdPercentage`: validates the current state var instead of the new param.

## Pipeline outcome
- **Enumeration (recall):** 224 candidate invariants over 35 functions, all 11 categories. On `moveLiquidity`:
  `cross_contract_consistency` + `role_access` (→ M-01) and `value_conservation` + `per_user_accounting` (→ M-02)
  were generated. `setProposalThresholdPercentage` was enumerated (→ M-03 category present).
- **Defense map:** 224 → DOES_NOT_COVER 112 · PARTIALLY_COVERS 78 · UNKNOWN_NEEDS_TRACE 30 · COVERS 4.
- **Autonomous validation (blind, no selection):** the `moveLiquidity` ordering/cross-contract invariant →
  **`NEEDS_EXECUTION`** with an exact fork test idea (the only human-actionable candidate). Everything else →
  `NEEDS_CONTEXT` (un-traced blind). **0 validated, 0 false promotions, 0 HYPOTHESIS_ONLY → POC_HANDOFF.**

## Ranking table (human-actionable)
| Rank | Function | Invariant | Decision | Maps to |
|---|---|---|---|---|
| 1 | `LiquidityManager.moveLiquidity` | ordering_race / cross_contract (permissionless migration price manipulation) | NEEDS_EXECUTION (+ fork test idea) | **M-01** ✓ |

## Metrics
**Recall:** relevant invariant *generated* — M-01 ✓, M-02 ✓, M-03 ✓, H-01 ✗ → **3/4**. Relevant invariant
*human-actionable* — M-01 ✓ → **1/4**. Relevant invariant **top-1** = M-01 ✓.
**Precision:** total generated 224 · validated_for_poc **0** · needs_execution **1** · false promotions **0** ·
decoys validated **0** · HYPOTHESIS_ONLY→PoC **0**.

## Failure analysis
- **H-01 — ENUMERATION SCOPE MISS:** the quorum numerator is a *constructor magic-constant*, not a function-level
  invariant the generator targets.
- **M-02 — VALIDATION/RANKING MISS:** the `value_conservation`/`per_user_accounting` invariant on `moveLiquidity`
  *was generated*, but blind validation left it `NEEDS_CONTEXT` (did not trace the raw-`balanceOf` injection);
  the sibling M-01 ordering invariant was surfaced instead.
- **M-03 — VALIDATION MISS:** `setProposalThresholdPercentage` *was enumerated* (cap_limit), but TokenGovernor
  functions weren't blind-traced → `NEEDS_CONTEXT`.
- **M-01 — HIT.**

## Honest caveats
- Validation reached **NEEDS_EXECUTION, not VALIDATED** — the blind-trace ceiling (P95/P97), exactly as predicted.
- The **lens *selection*** initially missed `moveLiquidity`; broad enumeration over all surfaced functions was
  needed → **selection is the dominant recall bottleneck**, not the per-function category generator.
- **One additive bug-fix mid-run:** the enumerator now also reads `source_text` (was `source_snippet`-only);
  backward-compatible, all P101 self-tests + suite (55) green. No frozen machinery / severity gate / threshold
  changed; no frozen eval artifact mutated.
- Per-candidate trace = **blind LLM-analyst reasoning over candidates (no invariant *selection*)** — the
  capability-bound step.

## Bottom line
On a fresh unseen subject, autonomous enumeration surfaced the correct invariant for the top migration finding
and the precision gates elevated it to the #1 human-actionable slot **without a human picking it and without
falsely promoting any decoy** — answering the primary question affirmatively at the recall+triage layer. Reaching
a *confirmed* finding remains gated by the human/fork PoC and by selection-layer recall (H-01 constructor-constant
and M-02/M-03 deep-trace misses).
