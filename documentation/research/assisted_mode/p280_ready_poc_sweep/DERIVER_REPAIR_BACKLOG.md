# P280 — DERIVER_REPAIR_BACKLOG (do NOT edit the deriver this phase)

| id | failed field | class | missing source-derived signal | owning repair | priority | FP risk |
|---|---|---|---|---|---|---|
| **D1** | attacker_path | ACCESS/ORDER | **inline `require(msg.sender==...)` / ownership `require(map[caller][..]>0)` guards** (not modifiers) | **inline-guard detection** (parse the source_span for inline caller/ownership requires; downgrade attacker_path to LOW when present) | **1** | low (reduces false READY) |
| D2 | attacker_path/impact | ACCESS (governor-like) | permissionless-by-design vs the real **state-machine** anomaly (accepted status set) | state-machine / invariant derivation (detect status-gate requires; flag accepted-state anomalies) | 2 | low |
| D3 | impact_delta/victim | ACCOUNTING/MATH/ORACLE | value-flow facts not in the manifest (already P279 backlog) | value-flow evidence derivation | 2 | medium |
| D4 | source_basis | all | the actual source_span text (the deriver used manifest metadata, not the body lines) | source-span extraction (read the function body lines, not just the manifest signature) | 3 | low |

**Headline:** before any READY-based PoC sweep is trustworthy, the deriver needs **inline-guard detection (D1)** — the
manifest `modifiers` field is not a sufficient auth signal. D1 + value-flow (D3) are the next repair phase.
