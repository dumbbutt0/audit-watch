# P214 — integrity precheck (START)

Behind default-off `AUDITWATCH_L3_READINESS`. No submit/route/promote/demote; human review mandatory.

## START hashes (md5 first-8)
| artifact | START | role |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | must NOT change |
| `scripts/min_confirm_gate.py` | `41dd3c96` | must NOT change |
| `scripts/confirm_gate.py` | `4fadfc5f` | must NOT change |
| `../hermes/memory/events.jsonl` | `fc446040` | must NOT change |
| `scripts/validate_p208_l3_readiness.py` | `7e148e18` | WILL change (carve-out in decide) |
| `scripts/submission_readiness_review.py` | `7c4b563d` | WILL change (l3_evaluate passthrough) |
| `scripts/dashboard.py` | `dbed5174` | WILL change (/api/p212 + p212.html field) |
| P208 `L3_READINESS_SCHEMA.json` | `91c0590f` | WILL change (additive fields) |

## Confirmations
- `AUDITWATCH_L3_READINESS` unset by default; `config/runtime_policy.json api_free=true`; no live route-to-submit;
  active audit quantamm (untouched). Baselines before edits: P208 backtest 10/10, P213 10/10, P210 tests 20+14.
