# P277 — REPAIR_METRICS

Backtest on the **P276 locus-mapped corpus** (144 awarded H/M, 7 contests). before = P276 (`metrics_BEFORE.json`,
locus-only, budget 5); after = P277 (`metrics_AFTER.json`, body signals, budget 5).

## Headline (LANDED: body signals, poc_budget=5)
| metric | before | after | delta |
|---|---|---|---|
| advisory_surfaced % | 68.1 | 68.1 | 0 |
| **class_routed %** | **39.6** | **41.7** | **+2.1** |
| mechanism_generated % | 39.6 | 41.7 | +2.1 |
| COVERAGE_CLASS_GAP (first_failed) | 41 | 38 | -3 |
| advisory-only non-awarded survivors | 39 | 35 | -4 |
| **severe concluded/reportable FP** | 0 | **0** | 0 |

## Attribution ablation (the honest part)
| run | class_routed % |
|---|---|
| A  before (budget 5, no body) | 39.6 |
| B  body, budget 5 (LANDED) | 41.7 |
| D  budget 8, NO body (ablation) | 51.4 |
| C  body, budget 8 | 53.5 |

- **Body signals alone = +2.1pp** — consistent at both budgets (B−A = 41.7−39.6; C−D = 53.5−51.4). Real, robust,
  modest. Body also reduced advisory-only survivor noise.
- **The poc_budget cap (5→8) is the DOMINANT lever (+11.8pp)** — a *separate* repair beyond R1's authorized scope.
  Not landed here; recommended as the next backlog item (see VERDICT/FP_REPORT).
- At budget 8, body even routed EXTERNAL_INTEGRATION (0→1) and helped DOS/ORDER — body's value grows once the budget
  stops being the binding constraint.

## Per-class (LANDED budget 5)
ACCOUNTING +1, SHARE +2, UNKNOWN_OTHER +10 (body filled locus-blank candidates), ACCESS −6 / DOS −4 (budget-5
round-robin reshuffle: body-elevated classes displace guard 2nd-reps — the reshuffle artifact that the budget repair
resolves).

## Weak classes are RECALL-bound, not coverage-bound
ORACLE_PRICING (0/4) and EXTERNAL_INTEGRATION (1/2) stayed 0 at budget 5 because their loci are **not surfaced**
(RECALL_GAP/MANIFEST_GAP) — a routing fix cannot route what recall never produced. They need R2/R3, not R1.
