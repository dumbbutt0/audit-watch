# P214 — carve-out scorecard

| case | flag-off | flag-on | expected | pass |
|---|---|---|---|---|
| SOPH-03 (all 10) | medium | **high** (applied) | high flag-on | ✅ |
| SOPH-03 missing any 1 criterion | medium | medium (blocked) | < high | ✅ (×10 parametrized) |
| not a carve-out candidate | medium | medium | < high | ✅ |
| l3_status NEEDS_HARNESS | (needs_harness) | not upgraded | < high | ✅ |
| source-refuted (all 10) | invalid | invalid | invalid | ✅ |
| production_source_modified | medium | not upgraded | < high | ✅ |
| human_judgment_required w/o notes | medium | blocked | < high | ✅ |
| malformed `{}` | (blocked) | fail-closed | < high | ✅ |
| non-DoS theft High | high | high (untouched) | high | ✅ |
| decent M-03 / vultisig M-03 / decent-06 | medium | medium | < high | ✅ (P213 set) |

SOPH-03 fixed flag-on; **0 new false-Highs**; flag-off output-equivalent; all negative controls hold.
