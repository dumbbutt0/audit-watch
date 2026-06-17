# Severity Mapping (documentation only)

Reference for the impact/severity gate. **This file is documentation; it is not
wired into any pipeline config.** The gate logic lives in
`submission/gates/gate_impact_severity.py` and mirrors the table below.

## Impact category → maximum supportable severity

| impact_category | Ceiling without strong PoC | With runnable+passing PoC and quantified delta |
|---|---|---|
| `fund_loss` | Critical | Critical |
| `governance_takeover` | Critical | Critical |
| `accounting_corruption` | High | Critical |
| `reward_extraction` | High | Critical |
| `fund_freeze` | High | Critical |
| `liveness_failure` | Medium | High |
| `dos` | Medium | High |
| `info` | Informational | Informational |

A claimed severity above the applicable ceiling is **severity inflation** →
`DO_NOT_SUBMIT` with a downgrade note naming the supportable severity. Re-file
at the supportable level instead of inflating.

## Immunefi v2.2 anchors

- MEV / direct theft of funds → **Critical**
- Protocol insolvency (users cannot redeem) → **Critical**
- Temporary freezing of funds → **High**
- Griefing / DoS without fund loss → **Medium**
- Best-practice / gas / code quality → **Low / Informational**

## Worst-case vs realistic-case

Every claim must separate the worst-case impact from the realistic-case impact
(`severity_justification.worst_case` and `.realistic_case`). A worst-case-only
justification triggers a human-review warning.
