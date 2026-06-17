# P222 — Integrity precheck (START)

Recorded `2026-06-07T17:24:15Z`. `config/runtime_policy.json` → `"api_free": true`. Research-only; no
external submission route; no submit/promote controls; L3 readiness flag (`AUDITWATCH_L3_READINESS`)
default-off unless set in-process.

## START hashes (md5)
| file | md5 |
|------|-----|
| scripts/dashboard_sync.py | 26bd7ee0bc2efdf31ca7c56c6f257558 |
| scripts/sync_hunt_findings.py | eb8c7d0383f3c430176ca8e483c88640 |
| scripts/submission_readiness_review.py | e49608787077c9ee39099017b8f4bcdc |
| scripts/finding_detail.py | 8e4ab621801c879dc825d65b2d201f91 |
| scripts/findings_overview.py | 5c6cccb57d0ae2528a0b57201aca9669 |
| scripts/funnel.py | d9f09981d9c6357d9c666a21bce48193 |
| scripts/dashboard.py | 197ac4d5180cec63f9fecaff46cd650a |
| scripts/validate_hunt_sync_completion.py | 00cf5f56fcad9858ffad1bf8846fde06 |
| scripts/run_hunt_sync_hook.py | 9e38136e526911d2d321d4ccd34f5229 |
| scripts/validate_p208_l3_readiness.py | fe37e6ad8069a9f83dbca3101ebcbb1c |
| documentation/research/funnel/synced_findings.generated.json | ac8978df368bcf03166b163cc213b8ab |
| output_research/l3_readiness/ZETA-04.json | 9fa27fa30b798956b81605cd734017e2 |
| output_research/l3_readiness/ZETA-10.json | e6b8eeeb2585b9e0d00bbe35fef087cb |
| output_research/l3_readiness/ZETA-11.json | 86b924071813858828e7078d574a7e32 |
| config/runtime_policy.json | bea434877f5f8b215e698fd5cdb9701e |

## Forbidden files (must stay byte-identical END)
| file | md5 |
|------|-----|
| prompts/deep_trace.md | ef93a6c220239c7ed96b790c2c6cd829 |
| scripts/min_confirm_gate.py | 41dd3c967080b9f7a07419984ed0f095 |
| scripts/confirm_gate.py | 4fadfc5f38cf39169267940884c3cd06 |

## `decide()` severity baseline (must be invariant END)
| candidate | calibrated_severity | high_promotion_allowed |
|-----------|--------------------|------------------------|
| ZETA-04 | medium | False |
| ZETA-10 | invalid | False |
| ZETA-11 | medium | False |

These are the values P222 must NOT move. `decide()` keys off `attacker_model`/`l3_status`/`impact_class`/
material-delta/control — never off `human_review_priority`, `reachability_class`, or `impact_type`.
