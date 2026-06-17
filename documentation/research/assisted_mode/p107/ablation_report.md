# P107 — Ablation report

From `sharp_plus_moderate`, each score feature is removed once. A feature is **eligible** iff its removal worsens top-k recall or mean rank, and including it does not materially worsen worst-case rank.

## Full-variant baseline (sharp_plus_moderate)
- top-3 20% · top-10 33% · mean 25.9333 · median 20 · worst 65

## Per-feature (effect of REMOVING the feature)
| Feature | Δtop-3 | Δtop-10 | Δmean rank | worsens top-k? | worsens mean? | inflates worst? | eligible |
|---|---|---|---|---|---|---|---|
| consequence_value_movement | -0.0667 | -0.0666 | 7.1334 | True | True | False | **True** |
| consequence_fund_reachability | -0.0667 | -0.0666 | 1.2667 | True | True | False | **True** |
| exploitability_external_call | -0.0667 | 0.0 | -1.4 | True | False | False | **True** |
| missing_update_asymmetry | 0.0667 | 0.2 | -1.3333 | False | False | False | **False** |
| state_write_breadth | -0.0667 | -0.1333 | 7.1334 | True | True | False | **True** |

**Eligible (earn their place):** ['consequence_value_movement', 'consequence_fund_reachability', 'exploitability_external_call', 'state_write_breadth']
**Not eligible (candidates to drop):** ['missing_update_asymmetry']

_Δ are (reduced − full): negative Δrecall means removing the feature HURT recall (so the feature helps); positive Δmean rank means removal pushed the awarded function DOWN (feature helps)._

