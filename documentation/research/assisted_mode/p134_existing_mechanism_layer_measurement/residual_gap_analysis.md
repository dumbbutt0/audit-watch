# P134 — True Residual Gap Analysis

After running the existing mechanism layer, the residuals are small and specific.

## Residual 1 — H-03 `NoyaValueOracle._getValue` (the only true DETECTOR_MISS)
- **Why the layer failed:** the bug is a **logic error** — the multi-hop loop advances `quotingToken=sources[i]`
  but feeds the static `asset` into each hop. It is not a units/decimals, aggregate, weighted-pool, or
  TVL-omission shape, so none of the value-computation mechanism taxonomies match it.
- **Class:** `needs-callgraph/depth or logic-trace` (identity/quantity-source divergence in a conversion loop).
- **Right fix:** **not a new static detector** — the existing in-session `deep_pass_value_provenance.md` /
  `depth_trace_v3.md` mechanism-trace prompt is designed for exactly "validated_subject vs mutated_subject /
  identity-source vs quantity-source divergence." Route H-03-class candidates (oracle multi-hop loops) through
  that deep-pass prompt. (P133's surface specialist already HIT it via the dead-variable smell, so it is
  human/prompt-catchable, just not static-detector-catchable.)
- **Priority:** low-medium (already catchable by surface review + the deep-pass prompt; no detector needed).

## Residual 2 — H-22 / H-15 / H-14 graded DETECTOR_PARTIAL (mechanism precision)
- **Why:** `arithmetic_conservation`/`units` flag the right function and the right *locus* (a ≥2-term aggregate /
  shares-assets / price-per-share) but not the **precise** error (Pendle composition, Silo shares-vs-assets,
  Balancer staked/held). For Silo, `semantic_tvl_completeness` even flags the **wrong** mechanism
  (collateral_debt_side_omission — but Silo does subtract debt).
- **Class:** `detector flags right function, incomplete mechanism` + (Silo) `wrong mechanism`.
- **Right fix:** **routing + deep-pass prompt**, not a new detector — surface the PARTIAL flag as advisory
  evidence and let the deep-pass mechanism trace resolve the precise error. A new detector would risk overfitting
  to these three composition shapes.
- **Priority:** medium (PARTIAL is already useful as a review pointer).

## NOT residual (well-covered)
- H-01 (decimals), H-13 (weighted-pool ÷), H-06 (omission), H-19 (debt sign), and bonus H-23/H-18 are all
  **detected**; their only issue is **routing** (Residual 3).

## Residual 3 — Routing/surfacing (the dominant gap; see routing_analysis.md)
- **Class:** `detector output is not routed`. units_invariant (report-only) and semantic_tvl_completeness
  (research-only) recover H-01 and H-06 but never reach review; CPA/AC escalate only in strict-full-audit.
- **Right fix:** routing/surfacing changes (advisory-evidence surfacing in the standard review package;
  human_review_queue context entries; research→advisory promotion after the 5-criteria bar). **No detector
  logic change.**
- **Priority:** high (cheapest, recovers the most).

## Summary
- **0 net-new mechanism detectors justified.** The class is covered (7/8 useful, 3/3 P133 MISS).
- The real work is **routing/surfacing** (Residual 3, high priority) + a **deep-pass prompt route** for the one
  logic residual H-03 (Residual 1) and the PARTIAL precision cases (Residual 2).
