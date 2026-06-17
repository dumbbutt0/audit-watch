# P213 — integrity checks (START == END)

## Production byte-identical START==END (none modified)
deep_trace.md `ef93a6c2` · min_confirm_gate.py `41dd3c96` · confirm_gate.py `4fadfc5f` ·
submission_readiness_review.py `7c4b563d` · dashboard.py `dbed5174` · validate_p208_l3_readiness.py `7e148e18` ·
ledger `fc446040`. ✓

## Research-only / un-wired
- `validate_p213.py` imports `decide()` READ-ONLY; `grep -rl validate_p213|p213_l3_dos_carveout scripts/ run_pipeline.sh
  config/ prompts/` → **none** (un-wired). Reads fixtures only; mutates no artifacts; no submit/route/promote.
- P212 Stage 1B/2 outputs + frozen blind candidates NOT rewritten. api_free=true. Active audit quantamm (untouched).

## Result
10/10 cases pass; SOPH-03 medium→High; new_false_highs=0; all negative controls < High. `metrics.json`/
`regression_cases.json` valid JSON. `fabrication_rate=0`. Decision: `DOS_CARVEOUT_VALIDATED_RESEARCH_ONLY`.
