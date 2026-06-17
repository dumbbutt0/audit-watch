# P238 — Hostile-token settlement lens: reNFT replay report

> Research-only detector `hostile_token_settlement` (un-wired). Replay on the frozen reNFT shadow workspace
> (`audits/renft-2024-01-shadow`, reusing the P237 coverage manifest). Recovery is mechanism-based (cleanup-verb +
> order-sourced token + missing containment), never answer-key string matching. Frozen P235 artifacts untouched.

## Candidates produced (2 total — both HIGH, 0 elsewhere)
| Contract.function | Conf | Shape | Maps to |
|---|---|---|---|
| PaymentEscrow._settlePayment | HIGH | hostile_token_settlement_dos | **H-01 (direct)** + **#64/#605 (same path)** |
| Reclaimer.reclaimRentalOrder | HIGH | hostile_token_settlement_dos | reclaim DoS (hostile rented token blocks reclaim → lock) |

`Stop.stopRent`/`stopRentBatch` correctly did NOT fire — their token transfers are cross-contract (in
PaymentEscrow/Reclaimer); the lens attributes the finding to the contract that holds the must-succeed transfer.

## Metrics
| Metric | Value |
|---|---|
| True recoveries (direct) | **1** — H-01 (`PaymentEscrow._settlePayment`: attacker-tipped consideration token, `_safeTransfer`, no try/catch → stopRent locks) |
| Partial / family recoveries | **#64 + #605** (blacklisting payment ERC20 / blacklisted lender) = the **same** settle path → covered by the PaymentEscrow candidate; plus **Reclaimer reclaim DoS** (related must-succeed-transfer vector, bonus) |
| False positives | **0** — caller's-own withdrawals, allowlisted/immutable assets, try/catch/pull-payment settles all suppressed |
| False negatives (in-family) | none observed on reNFT (settle + reclaim both caught) |
| False negatives (out-of-family, by design) | H-02/H-04/H-05 (Safe-management), H-03 (create-time reentrancy), #387 (Seaport invariant) — other families |
| Candidate volume / noise | **2**, both actionable, both in the settlement/reclaim family; **0 noise** (un-wired → nothing added to the production queue) |
| Precision (reNFT replay) | **2/2 = 100%** on the anchor (single-anchor caveat) |
| Weighted-recall gain vs P235 | adds H-01 (High=3) on top of P235's H-04; see COMBINED_RECALL_LIFT.md |
| Weighted-recall gain vs P237 | additive — P237 (Safe-mgmt) recovers H-02/H-04/H-05; P238 (hostile-token) recovers H-01/#64/#605; disjoint families |

## Precision iteration (honesty)
First full-manifest run was already low (1 candidate) but **under**-fired: `Reclaimer.reclaimRentalOrder` was wrongly
suppressed because the loose pull-payment marker `"owed"` matched **"all*owed*"** in `OnlyRentalSafeAllowed`. Fixed
to the record-debt form (`owed[`/`owed +=`/`debt[`); reclaim then recovered. No noise was ever introduced; this was a
false-negative fix, not a noise fix.

## Stop-and-report triggers — status
None fired. The lens is NOT generic token-noise (2/2 candidates on genuine cleanup paths; ordinary
deposit/swap/transfer functions and caller's-own withdrawals are suppressed by the 5-signal gate). Recovery
mechanism-based; no broad prompt rewrites; forbidden files byte-identical; no dashboard/routing/severity change.

## Recommendation: **validate both lenses across 15–20 targets**
The lens is clean on the anchor (0 FP, recovers H-01 + reclaim DoS) but single-anchor → stability =
PROMISING-BUT-NEEDS-REFINEMENT, not RESEARCH-STABLE; do **not** wire yet. With P237 (Safe-management) also built,
the right next step is a **joint 15–20 target validation campaign of both lenses** (per the user's intent to test
both recall lifts together), measuring 0-high-confidence-FP retention before any wiring decision. A second shadow
contest can follow the campaign to confirm the end-to-end recall lift on a fresh target before live hunting.
