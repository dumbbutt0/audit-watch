# P200 — controlled answer-key unseal log

Two-stage, double-freeze discipline. The answer key was opened in exactly two controlled steps, both recorded.

## Stage A — viability count-only (pre-sample)
- **badger-2024-06-holdout** (`_sealed_answer_key/report.md`): grepped severity section headers for **counts only**.
  Result: **2 Medium / 0 High / 0 Critical** (+ Low/QA). The header grep incidentally exposed the 2 Medium titles
  (markdown header = title) — recorded as a minor leak, but **badger was abandoned** (see CORPUS_VIABILITY) so it
  did not contaminate the scored corpus.
- **Survey of all sealed holdouts** (count-only, no titles): badger 2M/0H · centrifuge 8M/0H (used P198) · kleidi
  3M/0H · decent 4H/5M · munchables 2H/4M · pooltogether 1H/8M · **predy 4H/8M** · vultisig 3H/3M · zetachain 14H/34M.
  Only counts printed (no titles) → **predy blindness intact**.
- User selected **predy-2024-05-holdout** (4H/8M) as the substitute corpus.

## Stage B — full unseal (post-double-freeze, scoring only)
Opened `predy-2024-05-holdout/_sealed_answer_key/report.md` in full **only after**:
- FREEZE 1 (blind threat-ceiling verdicts) — hash `4aede343`
- FREEZE 2 (offline severity calibration) — hash `1e158f1e`

Awarded set extracted: **4 High (H-01..H-04) + 8 Medium (M-01..M-08)** — see `metrics.json` / `AWARDED` in
`scripts/validate_p200.py`. No source or corpus file mutated; seal opened read-only.

## Blindness attestation
- Blind subagents saw only frozen prompts (`deep_trace.md` + verbatim source); prompt leak-scan CLEAN.
- Raw-output leak-scan CLEAN (no finding-ID/issue-link cited by any agent).
- Offline calibration (RUBRIC_GRADES) was authored from each frozen output's own evidence **before** Stage B —
  the orchestrator had seen only predy's *counts* (4H/8M), never its finding bodies. Genuine out-of-sample.
