# P210 — integrity checks (END)

## Out-of-scope artifacts — byte-identical START==END
| artifact | hash |
|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` ✓ |
| `scripts/min_confirm_gate.py` | `41dd3c96` ✓ |
| `scripts/confirm_gate.py` | `4fadfc5f` ✓ |
| `scripts/final_submission_pack.py` | `57cba16d` ✓ |
| `scripts/validate_p208_l3_readiness.py` | `7e148e18` ✓ (imported, unchanged) |
| `../hermes/memory/events.jsonl` | `fc446040` ✓ |

## Intended changes (recorded)
| file | START | END |
|---|---|---|
| `scripts/submission_readiness_review.py` | `b435a635` | `7c4b563d` |
| `scripts/dashboard.py` | `1eb4e278` | `857d593a` |

## Guarantees
- Feature flag `AUDITWATCH_L3_READINESS` default-off; flag-off output-equivalent (14/14 existing tests unchanged;
  no `l3` key, no new blocker).
- L3 affects only High/Critical submission readiness; Medium/Low unaffected; discovery + min_confirm + confirm_gate
  unchanged; no submit/route/promote side effects; dashboard panel read-only.
- Malformed/missing L3 on High fails closed; human override requires written reason.
- `config/runtime_policy.json api_free=true` unchanged; canonical `submission_ready`/`routing_allowed` never flipped.
- Tests: flag-off 14/14, new L3 20/20, P208 backtest 10/10, no-submit guard pass. `fabrication_rate=0`; JSON valid.

## Decision
`L3_DARK_WIRING_READY`.
