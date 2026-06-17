# P189 — Cross-corpus validation of the P183–P188 adjudication stack

**Question:** does the deep-pass adjudication improvement (measured only on Quantamm: P184/P186 = 7/9) generalize
across architectures, or is it Quantamm-specific? **Read-only measurement.** No production/prompt/detector/answer-
key/corpus edits.

## Method (as approved)
- **Step 1 — DEEP_RUN_BUT_MISSED** per corpus: answer-key finding with `category=MISS`/`UNRECOVERED` whose function
  appears in the deep-pass **candidate queue** (the surface was routed to deep analysis). Pure discovery gaps
  (surface never routed to deep) are excluded from the denominator.
- **Step 2 — pre-registered bounded sample**: ≤4 misses/corpus, High→Medium, function-level locus first (rule and
  IDs written to `replay_results.json` before scoring).
- **Step 3 — blind re-adjudication**: production P188 `deep_trace.md` + verbatim source of the investigated
  surface, given to a blind **Sonnet** subagent (no answer key, no campaign memory). Prompts token-scanned before
  scoring (zero finding-IDs / answer-key text); raw outputs frozen verbatim; outputs token-scanned (zero answer-key
  IDs cited → blind confirmed). Scored answer-aware only after freeze; no backfill.
- **Quantamm = control** (P184/P186 7/9, reused, not re-run; excluded from the headline).

## DEEP_RUN_BUT_MISSED population (Step 1)
| corpus | total misses | deep-run misses | sampled |
|---|---|---|---|
| zaros | 62 | 23 (7 High) | 4 |
| revert-lend | 27 | 17 (4 High) | 4 |
| panoptic | 19 | 12 (2 High) | 4 |
| ark | 6 | 1 | 1 |

Note the macro signal already visible here: only ~40–60% of misses were ever deep-run; the remainder are
**discovery/coverage gaps** the adjudication stack cannot touch.

## Replay results (Step 3b) — 13 blind re-adjudications
| corpus | id | traced surface | outcome | feature / reason |
|---|---|---|---|---|
| zaros | H-01 | _handleWethRewardDistribution | **SELECTED** | inventory+carry-forward: incorrect WETH split selected |
| zaros | H-02 | stake | ENUMERATED_ONLY | accumulate/setActorShares ordering surfaced, not carried as the loss-of-value framing |
| zaros | H-07 | getCreditDepositsValueUsd | UNCHANGED_MISS | **sibling-trace** (awarded locus = getRealizedDebtUsd) |
| zaros | H-09 | getUnsettledRealizedDebt | UNCHANGED_MISS | **sibling-trace** (awarded = rebalanceVaultsAssets reverts) |
| revert-lend | H-02 | onERC721Received | **HARNESS_ESCALATED** | reentrancy via _cleanupLoan carried NEEDS_HARNESS |
| revert-lend | H-04 | execute | **SELECTED** | missing caller/ownership check selected #1 (exact) |
| revert-lend | H-05 | _getReferencePoolPriceX96 | **HARNESS_ESCALATED** | negative-tick truncation carried NEEDS_HARNESS |
| revert-lend | H-06 | _cleanupLoan | **SELECTED** | severity-floor: callback-revert blocks liquidation selected (exact) |
| panoptic | H-02 | settleLiquidation | ENUMERATED_ONLY | phantom-asset basis surfaced; reentrancy trigger in untraced sibling _liquidate |
| panoptic | H-03 | settleBurn | UNCHANGED_MISS | specific-mechanism miss (zero-premium commission-skip) |
| panoptic | M-02 | _getRequiredCollateralAtTickSinglePosition | **SELECTED** | credits-overwritten-not-accumulated selected #1 (exact) |
| panoptic | M-03 | twapEMA | UNCHANGED_MISS | specific-mechanism miss (wrong-order destructure) |
| ark | AK-M2 | withdrawTokens | UNCHANGED_MISS | specific-mechanism miss (non-receiver revert) |

Aggregate: **SELECTED 4 · HARNESS_ESCALATED 2 · ENUMERATED_ONLY 2 · UNCHANGED_MISS 5 · FALSE_CARRY 0.**

## The six questions, answered exactly
1. **Selection rate before P183–P188?** **0%** — by construction the sample are misses; the original pipeline
   selected none of these awarded mechanisms.
2. **Selection rate after replay?** **30.8% strict** (4/13 SELECTED); **46.2% surfaced** (6/13 SELECTED +
   HARNESS_ESCALATED); 61.5% appeared in some form (incl. ENUMERATED_ONLY).
3. **How many architectures improved?** **3 of 4** measured architectures had ≥1 SELECTED (zaros, revert-lend,
   panoptic). ark (n=1) did not. Quantamm control independently = 7/9.
4. **What caused the improvements?** Mechanism **inventory + carry-forward** (zaros H-01, revert-lend H-04,
   panoptic M-02), **severity-floor** discipline (revert-lend H-06 DoS-blocks-liquidation), and **harness-
   escalation** (revert-lend H-02 reentrancy, H-05 truncation carried NEEDS_HARNESS instead of dropped). These are
   exactly the P183–P188 features.
5. **Architecture-general or Quantamm-specific?** **Architecture-general.** Gains appear across perps (zaros),
   lending (revert-lend), and options (panoptic) — structurally unlike Quantamm's Balancer hooks — with
   **zero false carries**. Not concentrated in Quantamm-like systems.
6. **Now-dominant remaining failure mode?** **Two-layered, and adjudication is no longer the sole bottleneck:**
   (a) **upstream coverage / locus-routing** — at corpus level ~40–60% of misses were never deep-run, and 2/13
   sampled items traced the wrong sibling of a multi-function locus; (b) **specific-mechanism recall** — on
   correctly-traced functions the deep-trace enumerates plausible mechanisms but not the exact subtle awarded one
   (panoptic H-03, M-03, ark AK-M2).

## Decision: **PROMOTE_CONFIDENCE**
Improvement in ≥3 architectures · false_carry = 0 · gains spread across architecturally diverse systems (not
Quantamm-like). Per the framework this is `PROMOTE_CONFIDENCE`.

**Honest caveats (do not over-read):**
- Absolute selection rate is **modest** (30.8% strict); a real fraction is **HARNESS_BOUND** (2/13 → NEEDS_HARNESS,
  i.e. adjudication improved but execution uncertainty remains) — partial `HARNESS_BOUND` coloring.
- **Sibling-trace limitation:** 2 zaros items traced a sibling/leaf of a multi-function locus (an extraction/
  routing artifact, not an adjudication failure) — they depress the zaros rate.
- Blind outputs carried **high mechanism volume** (2 selected + 1–3 unresolved each); none clearly unsupported
  (false_carry 0), but volume is a precision watch-item.
- **before = 0 by construction**; Sonnet is same-vendor (residual caveat as P186); n≈4/corpus → architecture-level
  signal, not a precise recall figure.

## Bottom line
The phase **reduced generalization uncertainty**: the P183–P188 adjudication gain is **not a Quantamm artifact** —
it reproduces on three architecturally distinct corpora with zero false carries. But it also relocated the
frontier: the dominant remaining recall loss across these corpora is **upstream coverage/locus-routing** and
**specific-mechanism recall**, not adjudication.
