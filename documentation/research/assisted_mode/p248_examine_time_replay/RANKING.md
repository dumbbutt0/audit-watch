# P248 — Phase E: Ranking

Rank the four checkpoints by weighted recovery, implementation complexity, and FP risk → derive ROI for a
FIRST build. Complexity factor: LOW=1, MED=2, MED-HIGH=2.5. ROI = expected weighted recovery ÷ complexity
factor.

| Checkpoint | Expected wt recovered | Complexity | FP risk | **ROI (recovery/cost)** | Highs in cluster |
|---|---|---|---|---|---|
| **Accounting** | 2.8 | LOW (1) | LOW (mechanical: rounding dir / conservation / index / double-count) | **2.80** | 0 |
| State-transition | 4.5 | MED (2) | LOW–MED (adversarial "who-else/repeat/else-branch" can spawn speculative griefing candidates) | 2.25 | 2 |
| Permission | 2.1 | LOW (1) | LOWEST (binary structural mismatch: gated-principal vs affected-principal) | 2.10 | 1 |
| Cross-contract | 3.75 | MED–HIGH (2.5) | LOW–MED (cross-chain/external-protocol semantics) | 1.50 | 2 |

## Three orderings
- **By ROI (recovery per cost):** Accounting (2.80) > State-transition (2.25) > Permission (2.10) >
  Cross-contract (1.50).
- **By absolute recovery:** State-transition (4.5) > Cross-contract (3.75) > Accounting (2.8) > Permission
  (2.1).
- **By FP-tightness / determinism (lowest risk):** Permission ≈ Accounting > State-transition ≈
  Cross-contract.

## Sensitivity check
At GROSS (perfect checkpoint, no realization discount) the ROI of accounting (4.0) and state-transition (4.1)
are within noise — the #1 ROI slot is sensitive to the realization assumption. The robust tie-breaker for a
*first* build is therefore **risk and determinism**, not the razor-thin ROI gap: accounting (and permission)
are the most mechanical, FP-tightest, lowest-complexity operations.

## First-build choice
**Accounting** is the highest risk-adjusted ROI: top ROI ratio, the most deterministic/FP-tight operation,
and the lowest implementation complexity — the ideal way to validate the examine-time-checkpoint architecture
at minimal risk while banking real (~2.8 wt) recovery. **State-transition** is the highest *absolute*
recovery and recovers two reasoning Highs — it is the immediate second build (where High recall is recovered)
but costs ~2× and carries marginally higher FP risk, so it is not the lowest-risk first move.

Recommended build sequence (for the future, separately-approved implementation phase):
**1) Accounting → 2) State-transition → 3) Permission → 4) Cross-contract** (economic last / separate, only
real FP risk). Permission is a valid *co-first* if High-recall is prioritized over pure ROI (it recovers a
High at LOW cost / LOWEST FP), but its absolute recovery is the smallest.
