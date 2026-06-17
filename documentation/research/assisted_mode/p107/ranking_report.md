# P107 — Evidence-free ranking prototype: results

**Invariant:** Ranker: prioritize, don't promote.  ·  research-only, un-wired.  N findings = 15.

_Ranks are the position a human scanning the surface would reach the awarded function. Ties broken alphabetically so the baseline is exactly the P105/P106 status quo._

## Synthesis (the honest call)
- **OVERALL PASS: True** → proceed to P108: **True**
- Recommended variant = `['consequence_value_movement', 'consequence_fund_reachability', 'exploitability_external_call', 'state_write_breadth']` (SHARP + ablation-eligible moderates; net-harmful features dropped).
- Recommended beats baseline (top-3 ∧ top-10 ∧ median): **True**
- HS1 cross-contract-only tripped: False · HS3 ablation-fragility tripped: False
- HS2 net-harmful features (noisy-alone AND ablation-ineligible): ['missing_update_asymmetry'] — recommended excludes them: **True**
- Findings the ranker DEMOTES vs alphabetical (the honest cost, ≈ P106 FM-4): ['MUN-H-05', 'PHI-H-05', 'PHI-M-07', 'WLD-M-05']
- Evidence-free-unrankable under recommended (scored 0): []

## Verdict (primary criteria)
- **PASS: True** — a variant must beat alphabetical on top-3 recall AND top-10 recall AND median rank.
- Passing variants: ['sharp_only', 'sharp_plus_moderate', 'conservative', 'no_external_call_ablation', 'recommended']

## Variant comparison
| Variant | top-1 | top-3 | top-5 | top-10 | mean | median | worst | unrankable |
|---|---|---|---|---|---|---|---|---|
| alphabetical_baseline | 0% | 0% | 0% | 7% | 53.4 | 42 | 193 | 15 |
| sharp_only | 7% | 13% | 20% | 33% | 29.8 | 29 | 64 | 6 |
| sharp_plus_moderate | 7% | 20% | 20% | 33% | 25.9333 | 20 | 65 | 0 |
| conservative | 7% | 7% | 13% | 27% | 26.8 | 18 | 63 | 6 |
| no_external_call_ablation | 7% | 13% | 27% | 33% | 24.5333 | 14 | 64 | 0 |
| recommended | 7% | 27% | 40% | 53% | 24.6 | 10 | 77 | 0 |

## Per-architecture (awarded rank by subject)

_Showing variant: **recommended** (vs alphabetical_baseline)._
| Subject | finding | rank (variant) | rank (alpha) | surface |
|---|---|---|---|---|
| vultisig-2024-06 | VUL-H-01 | 1 | 15 | 31 |
| munchables-2024-07 | MUN-H-05 | 44 | 42 | 113 |
| traitforge-2024-07 | TRF-H-01 | 5 | 169 | 180 |
| traitforge-2024-07 | TRF-M-18 | 3 | 16 | 180 |
| phi-2024-08 | PHI-H-05 | 33 | 17 | 118 |
| phi-2024-08 | PHI-M-07 | 77 | 22 | 118 |
| kleidi-2024-10 | KLD-M-02 | 10 | 58 | 97 |
| ramses-2024-10 | RAM-M-02 | 7 | 40 | 68 |
| ramses-2024-10 | RAM-M-01 | 64 | 64 | 68 |
| wildcat-2024-08 | WLD-H-01 | 24 | 193 | 211 |
| wildcat-2024-08 | WLD-M-05 | 75 | 8 | 211 |
| secondswap-2024-12 | SS-H-01 | 4 | 45 | 85 |
| secondswap-2024-12 | SS-H-03 | 3 | 42 | 85 |
| secondswap-2024-12 | SS-M-11 | 16 | 27 | 85 |
| iq-ai-2025-01 | IQ-M-01 | 3 | 43 | 51 |

## Evidence-free-unrankable (scored 0 on the variant's features)
- recommended: []
- sharp_plus_moderate: []

## Hard-stop flags
- **HS1_cross_contract_only** — tripped: False
- **HS2_noise_over_signal** — tripped: True
- **HS3_ablation_fragility** — tripped: False

## Reading
- A win on top-3/top-10/median means evidence-free signals move the awarded function up the human's scan order without any validation.
- The unrankable set is the honest residual (P106 FM-4 access/index/cap/reward) — these need the validation layer (P108), not more ranking.

