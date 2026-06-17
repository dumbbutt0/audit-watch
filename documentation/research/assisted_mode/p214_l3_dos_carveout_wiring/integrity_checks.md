# P214 — integrity checks (START == END)

## Out-of-scope artifacts byte-identical START==END
deep_trace.md `ef93a6c2` · min_confirm_gate.py `41dd3c96` · confirm_gate.py `4fadfc5f` · ledger `fc446040`. ✓

## Intended changes (recorded)
validate_p208_l3_readiness.py `7e148e18→fe37e6ad` · submission_readiness_review.py `7c4b563d→e4960878` ·
dashboard.py `dbed5174→197ac4d5` · L3_READINESS_SCHEMA.json `91c0590f→415d3eeb` · output_research/l3_readiness/SOPH-03.json
(carve-out block added) · dashboard/p212.html (badge) · tests/research/test_l3_dos_carveout.py (new).

## Guarantees
Feature flag `AUDITWATCH_L3_READINESS` default-off; flag-off output-equivalent (P208 10/10, P210 20+14, SOPH-03 medium,
no carve-out keys). Flag-on: SOPH-03→High only with all 10; 0 new false-Highs; negative controls < High; source-refuted
invalid; malformed fail-closed. No submit/route/promote; canonical flags never flipped; active audit quantamm unchanged;
api_free=true. Stray dashboard test processes killed (0 running). `metrics.json` valid JSON; `fabrication_rate=0`.

## Decision
`DOS_CARVEOUT_DARK_WIRING_READY`.
