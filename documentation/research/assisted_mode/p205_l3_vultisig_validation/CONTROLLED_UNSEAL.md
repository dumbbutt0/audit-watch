# P205 — controlled answer-key unseal log (vultisig-2024-06-holdout)

## Stage A — count-only viability (pre-sample)
Grepped `_sealed_answer_key/report.md` section headers + severity-id tokens for **counts only** (no titles):
- `# High Risk Findings (3)` — line 119
- `# Medium Risk Findings (3)` — line 543
- `# Low Risk and Non-Critical Issues` — line 943
- High ids **3** · Medium ids **3** · (PCS: 3/3 contract-level + source-reachable, 2 qualifying).
Unseal boundary: section headers + id-token counts only. No finding bodies/titles read.

## Stage B — mapping unseal (post-FREEZE-1, Step 6)
After the blind run is frozen, the key is opened only to **map blind mechanisms → awarded High/Medium/false-positive
classes** for `L3_TARGET_MATRIX.md`. Recorded there.

## Blindness attestation
Blind subagents see only frozen prompts (`deep_trace.md ef93a6c2` + verbatim source); leak-scan required CLEAN. The
L3 standard is pre-registered before harness results. Harness verdicts are objective EVM executions.
