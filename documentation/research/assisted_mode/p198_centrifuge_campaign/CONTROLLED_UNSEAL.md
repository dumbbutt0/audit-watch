# P198 — controlled unseal (boundary record)

## Two-stage unseal discipline
- **Stage A (step 2, viability — MINIMAL):** read only severity-section **counts** from `report.md`. Commands:
  `grep -nE "Risk Findings|^# (High|Medium)"` → `# Medium Risk Findings (8)` (line 140); `grep -oE "\[[HM]-[0-9]+\]" | sort -u | wc -l` → 8.
  **Result: 0 High, 8 Medium.** Finding **titles and bodies were NOT read** at this stage.
- **Stage B (step 6, scoring — FULL, AFTER blind freeze):** the 8 Medium titles + bodies were read only **after**
  all 12 blind prompts and raw outputs were frozen and token-scanned. Used to build the awarded key and score.

## What was deliberately NOT read at viability (Stage A)
Finding titles, mechanisms, affected functions, the ~600 per-submitter JSONs, `report.md` bodies. The blind
subagents never received any of it (they got only their frozen prompt = `deep_trace.md` + verbatim source).

## Contamination control
The coverage manifest + the 12-surface bounded sample were derived from **source structure only** (invariant
density), frozen before any title/body was read. So even the orchestrator's Stage-B answer-awareness could not
bias the blind selection (subagents were blind; sample pre-registered from source). `fabrication_rate=0`.
