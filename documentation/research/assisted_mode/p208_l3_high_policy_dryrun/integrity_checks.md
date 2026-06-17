# P208 — integrity checks (START == END)

## Production artifacts — byte-identical START==END (NOT modified)
| artifact | START | END |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` ✓ |
| `../hermes/memory/events.jsonl` (ledger) | `fc446040` | `fc446040` ✓ |

No production prompt/checker/router/ledger/detector/dashboard/schema file modified. `config/runtime_policy.json`
unchanged (`api_free=true`; no live submission route).

## New artifacts (all un-wired, research-only)
- `scripts/validate_p208_l3_readiness.py` — carries `research_only=True`/`routes_in_production=False`; no
  run_pipeline/agent_policy/router reference; submits/routes/promotes nothing.
- `documentation/research/assisted_mode/p208_l3_high_policy_dryrun/` — policy, schema, fixtures, docs, metrics. Every
  fixture/schema carries `research_only:true`/`routes_in_production:false`.

## Backtest reproducibility
`python scripts/validate_p208_l3_readiness.py backtest` → 10/10 expected matches, 0 false-allows, 0 false-blocks,
schema 10/10 pass, 0 dashboard mismatches (`metrics.json`). Schema rejects malformed records
(`SCHEMA_FAIL: 'threat_ceiling' is a required property`). `fabrication_rate = 0` (each fixture cites its P204/P207
evidence artifact or is a clearly-labeled synthetic regression).

## Decision
`L3_POLICY_DRY_RUN_READY` — dry-run only, human review mandatory, no wiring.
