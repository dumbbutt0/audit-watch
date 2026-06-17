# P201 — controlled answer-key unseal log (zetachain-2023-10-holdout)

Double-freeze discipline; the answer key is opened in exactly two controlled steps.

## Stage A — viability count-only (pre-sample, Step 4)
Grepped `_sealed_answer_key/report.md` section headers + severity-id tokens for **counts only** (no finding titles
printed). Result:
- **High Risk Findings (14)** — lines 87–2016
- **Medium Risk Findings (34)** — lines 2017–5469
- Low/Non-Critical — line 5470+
- Critical 0 · High **14** · Medium **34** · Low(id-tokens) 0
Exact unseal boundary recorded above. No finding bodies/titles read. Corpus VIABLE (≥1 High; severity-rich).

## Stage B — full unseal (post-double-freeze, scoring only, Step 7)
Will open `report.md` in full **only after** FREEZE 1 (blind verdicts) and FREEZE 2 (refined calibration) hashes
are recorded. Awarded set extracted there; no source/corpus mutation; seal read-only.

## Blindness attestation
- Blind subagents see only frozen prompts (`deep_trace.md ef93a6c2` + verbatim source); prompt leak-scan required CLEAN.
- Raw-output leak-scan required CLEAN (no finding-ID/issue-link).
- Refined calibration (RUBRIC_GRADES) authored from each frozen output's own evidence **before** Stage B — the
  orchestrator has seen only zetachain *counts* (14H/34M), never finding bodies. Genuine out-of-sample.
