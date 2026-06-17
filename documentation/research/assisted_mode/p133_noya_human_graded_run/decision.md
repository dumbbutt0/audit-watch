# P133 — Decision

## Decision: **RECALL_REAL_BUT_DEPTH_BOUND**

The P130 boost (trimmed in P132) delivers **real, boost-attributable recall** on noya — but bounded by
mechanism depth, not by visibility. An informed specialist review of the 8 newly-visible awarded functions
catches **5/8 useful (2 HIT + 3 PARTIAL)**; the remaining **3/8 are visible-but-MISS** (subtle weighted-pool
math and oracle decimals that need a deeper pass). The boost adds **zero speculative FPs** — its only cost is
reviewer load (39 on-class human-queue items).

### Why this label
- Not **RECALL_FULLY_REALIZED**: only 2/8 HIT, 3/8 MISS — visibility ≠ capture for subtle mechanisms.
- Not **RECALL_NOMINAL**: the boost is *necessary* (without it all 8 score 2 → clear-biased cheap-sweep → 0
  recall) and yields 5/8 useful detection incl. 2 clean HITs (Morpho sign error, NoyaValueOracle loop-var).
- Matches the answer key's own discoverability hypothesis (TVL omission/composition surfaceable; subtle ÷ +
  oracle decimals MISS), with 2 refinements graded HIT.

## Final response

**What was measured**
- Recall (answer-key-graded, informed = upper bound): boost-delta awarded **HIT 2 / PARTIAL 3 / MISS 3** →
  **useful 5/8 (62%)**, strict 2/8 (25%), vs an 8/8 visibility ceiling → **deep-reasoning gap 3/8**.
- FP: **speculative-FP rate 0**; 52 non-awarded boosted → 39 needs_human (on-class), 13 clear, 0 reject.

**Awarded recall preservation** — all 8 P131/P132 awarded functions present in the trimmed delta and reviewed;
2 confirmed (HIT), 3 partial, 3 visible-but-missed.

**FP / reviewer load** — 0 fabricated flags; 39 legitimate on-class review items routed to the sanctioned
`human_review_queue.jsonl` (true valid/FP split human-deferred); no `arithmetic`/`economic_attack` over-fire.

**Control / integrity** — no production code changed (review-only); `rank_signal_probe --self-test` OK; full
suite 1586 passed / 2 pre-existing snapshot fails / 4 skipped (unchanged); active audit never switched
(`quantamm-2024-12-eval`). No AI valid/FP verdict on non-awarded findings.

**Honesty limits** — recall grades are informed (answer key read) → upper bound; a blind run is ≤ this (MISS
grades robust, HIT/PARTIAL optimistic). The 39-item human queue is the un-measured FP remainder.

**Decision** — RECALL_REAL_BUT_DEPTH_BOUND.

**Next recommended phase (P134)** — two complementary directions: (a) a **deep-pass mechanism layer** for the
visible-but-MISS class (weighted-pool valuation, multi-hop oracle decimals/units) to convert PARTIAL/MISS → HIT
— this is where the remaining recall lives, and it is depth (not coverage) work; (b) a genuine **human grading**
of the 39-item queue to turn FP-tendency (0 speculative) into a measured valid/FP rate. Coverage (P130-133) has
done its job; the frontier is now mechanism-depth + human FP grading.
