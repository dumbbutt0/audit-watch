# P213 — integrity precheck (START)

Research-only severity-mapping repair; validation-first; NOT wired. No submit/route/promote/demote.

## START hashes (md5 first-8) — byte-identical at END
| artifact | hash |
|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` |
| `scripts/min_confirm_gate.py` | `41dd3c96` |
| `scripts/confirm_gate.py` | `4fadfc5f` |
| `scripts/submission_readiness_review.py` | `7c4b563d` |
| `scripts/dashboard.py` | `dbed5174` |
| `scripts/validate_p208_l3_readiness.py` | `7e148e18` |
| P208 `L3_READINESS_SCHEMA.json` | `91c0590f` |
| `../hermes/memory/events.jsonl` | `fc446040` |

## Confirmations
- `config/runtime_policy.json api_free=true`; no live route-to-submit; active audit quantamm (untouched).
- This phase writes only under `p213_l3_dos_carveout/`; the helper `validate_p213.py` imports `decide()` READ-ONLY
  (for `old_label`) and is NOT imported by production. P212 Stage 1B/2 outputs + frozen blind candidates NOT rewritten.
- SOPH-03 L3 record basis: `l3_status=FAIL, impact_class=dos, attacker=permissionless` → old `decide()` → `medium`
  (the under-rating to repair).
