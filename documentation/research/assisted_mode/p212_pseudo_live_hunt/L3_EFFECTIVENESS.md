# P212 Stage 2 — L3 effectiveness on a live target

## Where L3 helped (precision / false-High avoidance) — GOOD
- SOPH-01, SOPH-02: the harness layer **refuted** both over-claimed "Highs"; neither is an awarded finding → correct
  **true negatives**, 0 false-Highs shipped.
- SOPH-04 (likely by-design) + SOPH-05/06/07 (privileged): correctly **not promoted**; none awarded (Sherlock
  invalidates pure admin-input). 0 false positives overall.

## Where L3 hurt (severity floor too low) — REGRESSION
- SOPH-03 / 003-H: L3 **confirmed the bug** (recall win) but its severity rule **capped a genuine High at Medium**.
  The "DoS not theft → Medium" demotion is too aggressive for a **permanent, core-functionality DoS**.

## Net
L3 precision/refutation worked (0 false-Highs, correct true-negatives), but the L3 **severity calibration
under-rated the one confirmed High**. The standard needs a carve-out: *permanent DoS of a core deposit/withdraw path
(no admin prereq) can be High*, not auto-Medium. This is the actionable fix from the first pseudo-live hunt.
