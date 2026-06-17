# P192 — Locus-resolution validation + deep-pass selection-consistency audit

**Validates P191's two load-bearing assumptions** before any routing/scoring change. **Read-only**, deterministic,
no model runs. Every recovered match cites an artifact; unknowns stay `UNKNOWN`.

## Decision: `MEASUREMENT_NOISE_PRIMARY`
A majority (54.2%) of P190's "discovery" loss resolves to a real manifest function under a deterministic ladder —
so it was **measurement noise, not coverage failure** — confirming P191's reframe. A real but **secondary**
deep-pass selection inconsistency exists (revert-lend), so Question B is mixed; it is not the primary lever.

## Question A — locus-resolution recoverability (ladder over 59 P190 discovery findings)
| tier | n | confidence |
|---|---|---|
| TIER0_EXACT | 1 | exact |
| TIER1_NORMALIZED | 1 | high |
| TIER2_FUZZY (contract-constrained ≥0.85) | 9 | candidate |
| TIER3_ALIAS (fn name present in answer-key title/alt_titles or eval match_terms) | 21 | candidate (artifact-cited) |
| TIER4_UNRESOLVABLE | 27 | — |

- **Resolved to a real function: 32/59 = 54.2%** → that share of P190 "discovery loss" is measurement noise.
- **Unresolvable: 27/59 = 45.8%** survives even the full ladder.
- The dominant recovery mode is **TIER3_ALIAS (21)**: the answer key *named the function in its title/alt_titles*
  (e.g. zaros H-05 `settleVaultsDebt`, H-06 `withdrawUsdTokenFromMarket`) or eval `match_terms` carried it (H-04
  `getVaultCreditCapacity`) — our `affected_functions` extraction simply missed it. **TIER2_FUZZY (9)** is
  get/set naming drift (`autoDeleverageFactor`→`getAutoDeleverageFactor`). Only **2** are exact/normalized.
- **Honesty:** Tier-2/3 are *candidate* resolutions (artifact-cited, not human-confirmed). A "resolved" finding
  means the awarded function is **locatable in the manifest** — it downgrades the discovery loss to measurement
  noise, but does **not** prove the pipeline would have caught the bug.

## Question B — deep-pass selection consistency (kind=function)
| corpus | status | evidence |
|---|---|---|
| panoptic | **CONSISTENT** | deep-run scores 2–5, every skipped queued fn = score 2 (monotone) |
| revert-lend | **INCONSISTENT** | `withdraw` (score 5) skipped while `mint`/`borrow`/`repay` (score 4) deep-run |
| zaros | UNKNOWN | no `deep` pass executed (0 deep items) |
| ark | UNKNOWN | no `deep` pass executed |

**Priority-starvation attribution (9 P191 cases): 9/9 `routing_heuristic_overrode_score`** — in every case a
function with score ≤ the awarded function's score was deep-run while the awarded (queued) function was skipped. So
where deep-pass ran, selection is **not** a clean top-N-by-queue-score; a heuristic (richer `selected_by` /
different ordering) overrides the computed score. But this is **corpus-dependent** (panoptic consistent), so it is
a real secondary problem, not the dominant one.

## The six required answers
1. **% of P191 discovery loss that survives improved resolution:** **45.8%** (27/59 remain `UNRESOLVABLE`).
2. **How much discovery loss was measurement noise:** **≥54.2%** (32/59 resolve to a real function), overwhelmingly
   because the answer key already names the function in its text (Tier-3 alias) or via get/set naming drift
   (Tier-2) — i.e. a locus-**extraction** gap, not a pipeline coverage gap. Only 2 were exact.
3. **Does deep-pass follow queue ranking?** **Not reliably.** revert-lend is INCONSISTENT (clear score inversions),
   panoptic is CONSISTENT, zaros/ark ran no deep pass (UNKNOWN). It is corpus-dependent.
4. **Are starvation cases score-driven or heuristic-driven?** **Heuristic-driven** — 9/9 had a ≤-scored function
   deep-run while the higher/equal-scored awarded function was skipped.
5. **Real upstream bottleneck after measurement noise is removed:** much smaller than P190 implied. The residual is
   **(a)** the genuinely-unresolvable ~46% (27 findings — possible real coverage gaps, but unconfirmable from
   artifacts without source inspection) and **(b)** deep-pass selection not respecting its own queue score in at
   least one architecture (revert-lend). The "discovery bottleneck" is mostly a **measurement/extraction** problem.
6. **What should P193 target?** **Answer-key → function locus resolution / extraction first** — it cheaply removes
   ≥54% of the discovery bucket (capture function names from title/alt_titles/match_terms = Tier-3; handle get/set
   drift = Tier-2) and is prerequisite to honestly sizing the real gap. **Then** deep-pass selection-by-score
   consistency (the revert-lend inversions). **Not** queue depth, and not ranking calibration yet. Note: the
   highest-value P193 work (a) is largely **eval-harness/measurement** infrastructure, not production routing.

## Honesty / limits
- `MEASUREMENT_NOISE_PRIMARY` is partly a statement about the **eval answer-key→function mapping**, not only the
  production pipeline: most "discovery loss" is the harness failing to extract a function name the answer key
  already contains. Fixing it is a measurement correction that shrinks (does not necessarily eliminate) the gap.
- Tier-2/Tier-3 recoveries are candidate-grade; the high-confidence (exact/normalized) recovery is only 2/59. The
  54.2% should be read as "locatable in artifacts," not "confirmed correct function."
- Question B is genuine only for revert-lend/panoptic (zaros/ark ran no deep pass). n is small → directional.
- `fabrication_rate=0`; every resolution and inversion cites the exact artifact field/value.
