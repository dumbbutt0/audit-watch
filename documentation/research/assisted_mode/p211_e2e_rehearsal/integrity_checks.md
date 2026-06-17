# P211 — integrity checks (START == END)

## Production artifacts — byte-identical START==END (none modified in P211)
| artifact | hash |
|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` ✓ |
| `scripts/min_confirm_gate.py` | `41dd3c96` ✓ |
| `scripts/confirm_gate.py` | `4fadfc5f` ✓ |
| `scripts/submission_readiness_review.py` | `7c4b563d` ✓ (P210 END) |
| `scripts/dashboard.py` | `857d593a` ✓ (P210 END) |
| `scripts/final_submission_pack.py` | `57cba16d` ✓ (NOT modified) |
| `scripts/validate_p208_l3_readiness.py` | `7e148e18` ✓ |
| `../hermes/memory/events.jsonl` | `fc446040` ✓ |

## Guarantees
- Known corpus (decent), not a live bounty; nothing submitted/routed/promoted.
- Active audit remained `quantamm-2024-12-eval` (not switched, not scored).
- `AUDITWATCH_L3_READINESS` set only in-process for flag-on steps; unset at END; never persisted to config.
- `config/runtime_policy.json api_free=true` unchanged.
- Flag-off output-equivalent to pre-P210; flag-on blocks High-without-L3 only; Medium unaffected; dashboard read-only.
- `record_review` never set `submission_ready`/`routing_allowed=true`; rehearsal rows removed from the shared research
  ledger afterward (pre-existing row preserved).
- L3 records written only under `output_research/l3_readiness/` (audit-independent loader location).
- `metrics.json` valid JSON; `fabrication_rate=0` (every result from a real function call / forge-backed P204/P207 record).

## Decision
`E2E_REHEARSAL_READY_FOR_REAL_HUNT`.
