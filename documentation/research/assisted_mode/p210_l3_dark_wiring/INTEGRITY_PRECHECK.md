# P210 — integrity precheck (START)

Implementation phase; default-off feature flag `AUDITWATCH_L3_READINESS`. Non-submitting, advisory/readiness-only.

## START hashes (md5 first-8)
| artifact | START | role |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | must NOT change |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | must NOT change |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | must NOT change |
| `scripts/min_confirm_gate.py` | `41dd3c96` | must NOT change |
| `scripts/confirm_gate.py` | `4fadfc5f` | must NOT change |
| `scripts/final_submission_pack.py` | `57cba16d` | must NOT change |
| `scripts/validate_p208_l3_readiness.py` | `7e148e18` | imported (must NOT change) |
| `../hermes/memory/events.jsonl` (ledger) | `fc446040` | must NOT change |
| `scripts/submission_readiness_review.py` | `b435a635` | WILL change (L3 wiring) |
| `scripts/dashboard.py` | `1eb4e278` | WILL change (read-only L3 panel) |

## Confirmations
- `config/runtime_policy.json api_free=true` (unchanged) → no live route-to-submit.
- No historical artifact will be rewritten; overlay stays append-only; canonical `submission_ready`/`routing_allowed`
  never flipped.
- Baseline: `tests/research/test_submission_readiness.py` = 14 passed (pre-change).
