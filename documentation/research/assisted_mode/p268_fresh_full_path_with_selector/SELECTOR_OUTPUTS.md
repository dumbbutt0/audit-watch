# P268 — SELECTOR_OUTPUTS (Phase 6)

The **frozen P267 selector** (`mechanism_pairwise_selector.py`, `b0623b8c88752059`) run over each B/C top-2 pair.
Dimensions assigned BLIND from karak source, pre-reveal (selector input `outputs/p268_selector_input.json`;
decisions `outputs/p268_selector_decisions.json`; guard PASS, 0 violations).

| case | outcome | anti-easy-PoC | impact gap | terminal-impact (M1 vs M2) | decisive |
|---|---|---|---|---|---|
| **C1 redeem** | **KEEP_BOTH** | **YES** | 7 | 10 vs 3 | terminal-impact dominance; both plausible → protect high-impact before PoC; anti-easy-PoC: don't drop M1 for the easier M2 |
| **C2 mint** | **KEEP_BOTH** | **YES** | 8 | 9 vs 1 | same — preserve the inflation mechanism over the dust-rounding rival |
| C-neg slashing | **REFUTE_M1_FIRST** | no | 7 | 10 vs (refuted) | high-impact but **refuted** (Core-gated) → refute before trusting; control held (no finding manufactured) |

## Effect (the P268 measurement)
- **The P266 drop is FIXED:** on both real pairs the raw pre-P267 path would have selected the easier M2 and dropped
  the higher-impact M1. P267 returns **KEEP_BOTH**, so **both C1-M1 (finishRedeem accounting) and C2-M1 (inflation)
  are carried into five-op completion + PoC** — they are no longer dropped before PoC.
- **Budget:** KEEP_BOTH on C1 and C2 → up to 4 mechanisms to completion (M1+M2 each). Within the 2–4 PoC budget if
  focused on the two M1s; the two M2s (approval-revert, dust-rounding) are low-impact and completed lightly/at lower
  priority. No high-impact mechanism is skipped for budget.
- **Negative control:** C-neg → REFUTE_M1_FIRST — the selector does not push the gated slashing path into PoC as a
  finding; it demands refutation first (and the gating refutes it). The selector is not a "promote everything" stage.

Falsification questions carried forward: C1-M1 — does a snapshot rate at startRedeem (vs finish-time spot) neutralize
manipulation? C2-M1 — does solady's `_useVirtualShares()` default neutralize inflation? Both resolved in
completion/PoC. Frozen before completion.
