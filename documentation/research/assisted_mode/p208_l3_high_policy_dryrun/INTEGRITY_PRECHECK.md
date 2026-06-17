# P208 — integrity precheck (START)

Dry-run policy phase. No auto-submit, no live routing, no promotion/demotion of real findings, no canonical-label
or answer-key change. Production prompts/checker/router/dashboard NOT modified (policy ships as a standalone un-wired
validator + schema + docs).

## START production hashes (md5 first-8) — must be byte-identical at END
| artifact | hash |
|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` |
| `../hermes/memory/events.jsonl` (ledger) | `fc446040` |

(No dashboard/schema production files are touched, so none are listed for modification.)

## Evidence artifacts confirmed present (backtest inputs)
- `documentation/research/assisted_mode/p204_l3_magnitude_standard/metrics.json` ✓
- `documentation/research/assisted_mode/p207_vultisig_l3_dependency_assembly/metrics.json` ✓

## Live-route confirmation
- `config/runtime_policy.json` → `api_free=true` → no live Anthropic/submission route enabled.
- New artifacts carry `research_only:true` / `routes_in_production:false` (platform hard rule).
- The new validator `scripts/validate_p208_l3_readiness.py` is un-wired (no run_pipeline/agent_policy/router reference).
