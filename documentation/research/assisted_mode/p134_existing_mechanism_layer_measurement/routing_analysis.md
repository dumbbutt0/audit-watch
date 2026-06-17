# P134 — Routing Analysis

The headline: the detectors **catch** the P133 MISS class, but the recovering outputs largely **don't reach
human review**. The gap is routing, not detection.

| Recovered awarded | Recovering detector | Current routing | Reaches review? | Recommendation (non-submission) |
|---|---|---|---|---|
| H-13 Balancer (MISS→HIT) | connector_position_accounting | advisory via `advisory_escalation_gate`, **strict-full-audit only** | only in strict full audit | **surface as advisory evidence** in the standard review package (not just strict mode) |
| H-19 Morpho (HIT) | connector_position_accounting | advisory (strict-full-audit only) | only in strict full audit | same |
| H-14/H-22/H-15 (MISS/PARTIAL) | arithmetic_conservation | advisory (strict-full-audit only) | only in strict full audit | surface as advisory evidence |
| H-01 Chainlink (MISS→HIT) | units_invariant | **report-only** | **no** | **add to human_review_queue as non-submission-ready context** (report exists, nobody sees it) |
| H-06 Aerodrome (PARTIAL→HIT) | semantic_tvl_completeness | **research-only / un-wired** | **no** | **promote research→advisory after more tests** (1 clean noya recovery; needs the 5-criteria bar) — until then, surface its report as advisory evidence in review |
| H-23/H-18 (bonus) | registry_position_lifecycle | research-only | no | keep research-only (already research-stable; same promotion bar) |

## Findings
1. **connector_position_accounting + arithmetic_conservation** are wired but only fire into review under
   **strict full-audit** mode (`advisory_escalation_gate` strict gates). In a normal run their high/medium hits
   (incl. the H-13 Balancer recovery) are computed but not escalated → **surfacing gap**.
2. **units_invariant** is **report-only**: it correctly flags H-01 chainlink_decimals but the report is never
   surfaced to the human review queue → **the recovery is invisible**.
3. **semantic_tvl_completeness** is **research-only/un-wired**: it cleanly recovers H-06 (omission) but by design
   never routes → **invisible without promotion**.
4. No recommendation promotes anything to **submission-ready** (constraint 6). All recommendations are
   advisory-evidence / human-queue-context / research→advisory-after-tests.

## Net
The existing layer's detection is strong (7/8 useful, 3/3 MISS); its **review-surfacing is weak** (2 of the 3
MISS-recovering detectors don't reach review at all, and the advisory ones only in strict mode). The cheapest,
highest-value next work is **routing/surfacing**, not new detectors.
