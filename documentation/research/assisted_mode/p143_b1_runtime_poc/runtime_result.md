# P143 — Runtime Result

| field | value |
|---|---|
| harness_type | **real_contract** (real `NoyaValueOracle` deployed; real `getValue` called) |
| tests | 4 passed / 0 failed / 0 skipped |
| vulnerable_output | **20e18** (real contract, route [B,C]) |
| corrected_output | **6e18** (loop-carried reference) |
| delta | 14e18 |
| ratio | 20/6 = **3.33×** over-valuation |
| single_hop_control | real == corrected == 6e18 (no divergence) |
| equal_price_control | real == corrected == 6e18 (divergence vanishes) |
| runtime_status | **runtime_confirmed** |
| runtime_confidence | high |

## What this proves
The real `NoyaValueOracle.getValue` over-values a 2-hop route by 3.33× because hop i=1 prices `asset→C` (10)
instead of `quotingToken(B)→C` (3). The two controls isolate the cause: a single-hop route and an
equal-per-hop-price 2-hop route both show zero divergence, so the discrepancy is caused specifically by the
static-`asset` hop when per-hop oracle paths differ — exactly the prompt-derived mechanism.

## What it does NOT prove (kept honest)
- **Severity / economic impact** in the live protocol (which routes have ≥2 sources with materially different
  per-hop oracles, and what downstream accounting consumes the mis-value) — not assessed; needs human review.
- **Reachability under real maintainer-configured routes** — the PoC configures routes via the real setters with
  a stub registry; whether production deployments actually register ≥2-source divergent routes is a scope/human
  question.
- Nothing here is a submission; see safety_review.md.
