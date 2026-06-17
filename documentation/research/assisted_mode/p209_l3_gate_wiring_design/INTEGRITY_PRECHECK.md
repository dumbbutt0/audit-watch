# P209 — integrity precheck (START)

Design-only phase. No wiring, no live-routing change, no submit, no auto-promote/demote, no canonical-label change,
no production behavior change beyond read-only inspection + the existing P208 read-only backtest probe.

## START hashes (md5 first-8)
| artifact | hash | role |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | production prompt (must not change) |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | checker (must not change) |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | resolver (must not change) |
| `../hermes/memory/events.jsonl` | `fc446040` | ledger (must not change) |
| `scripts/min_confirm_gate.py` | `41dd3c96` | field-presence gate (inspected read-only) |
| `scripts/confirm_gate.py` | `4fadfc5f` | reachability-truth gate (inspected read-only) |
| `scripts/submission_readiness_review.py` | `b435a635` | readiness overlay (inspected read-only) |
| `scripts/dashboard.py` | `1eb4e278` | dashboard (inspected read-only) |
| `scripts/validate_p208_l3_readiness.py` | `7e148e18` | P208 dry-run validator (probe only) |
| `p208_…/L3_READINESS_SCHEMA.json` | `91c0590f` | P208 schema |

## Confirmations
- `config/runtime_policy.json` → `api_free=true` (unchanged) → no live Anthropic/submission route.
- No live route-to-submit enabled; `submission_ready`/`routing_allowed` are display/false everywhere
  (`finding_detail.py`/`findings_overview.py` stamp them false; `submission_readiness_review.py` never flips them).
- P209 writes only under `documentation/research/assisted_mode/p209_l3_gate_wiring_design/`. No source edited.
