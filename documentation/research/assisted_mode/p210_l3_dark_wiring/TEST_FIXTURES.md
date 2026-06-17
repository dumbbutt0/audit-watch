# P210 — test fixtures

Reuses the P208 records (single source of truth) + 2 new human-override cases under `fixtures/`.

| fixture | source | target | expected |
|---|---|---|---|
| decent H-01 setRouter-mint | p208/backtest | High | clear (allowed) |
| vultisig H-01 claim-fee-loss | p208/backtest | High | clear (allowed) |
| decent M-03 receiveFromBridge | p208/backtest | High | blocked_by_missing_l3_poc |
| vultisig M-03 cap-bypass | p208/backtest | High | blocked_by_missing_l3_poc |
| static_high_no_poc | p208/regression | High | blocked |
| (empty / None / GARBAGE / non-record) | inline | High | fail-closed (blocked) |
| Medium target (no record) | inline | Medium | not gated (allowed) |
| human_override_with_reason | p210/fixtures | High | allowed + override marked |
| human_override_without_reason | p210/fixtures | High | blocked (no rationale) |

P208 parity set = 10 backtest+regression records (decide target-independent).
