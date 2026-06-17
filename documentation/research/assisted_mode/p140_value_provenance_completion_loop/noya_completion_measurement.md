# P140 — Noya Completion Measurement

Measured on the two P139-queued noya jobs. Active audit switched to noya for the run, then restored.

## Setup
- Regenerated the 2 P139 jobs via `run_value_provenance_advisories.py` (build) against noya's
  `mechanism_advisory_context.json` (10 `deep_pass_value_provenance` recs → 2 jobs, 8 skipped — config-setters
  excluded by the P139 trigger):
  - `VP-NoyaValueOracle._getValue`
  - `VP-SolvencyV2.convertAmountsToValues`
- Created **one real** manual artifact for `NoyaValueOracle._getValue` sourced from the **P137 blind deep-pass
  result** (`execution_mode=manual_in_session`, `reviewer_or_runner="P137 blind subagent"`, `source_result_path`
  = the P137 deliverable, `prompt_decision=finding`, `confidence=high`, neutral mechanism summary — **no
  answer-key issue IDs**). This is a genuine prior in-session deep-pass output, not fabricated.
- Left `SolvencyV2.convertAmountsToValues` **pending** (no fresh run executed → not fabricated).

## Result of `--ingest-results`
| Metric | Value |
|---|---|
| accepted | 1 (`VP-NoyaValueOracle._getValue`) |
| rejected / quarantined | 0 |
| unmatched | 0 |
| completed | 1 (finding) |
| pending_remaining | 1 (`SolvencyV2.convertAmountsToValues`) |
| by_decision | `{finding: 1}` |

## Advisory safety fields (both entries, post-ingest)
`advisory_only=true`, `submission_ready=false`, `requires_human_review=true` — preserved/forced.

## Review-gate rendering (`review_gate_noya.md`)
- Subsection "### Value Provenance Deep-Pass Results — advisory only" present with the disclaimer.
- `NoyaValueOracle._getValue` → `completed | finding — NOT confirmed | high | build_poc | <mechanism>`.
- `SolvencyV2.convertAmountsToValues` → `pending_manual_execution | pending`.
- **Confirmed findings: 0 (unchanged).**
- `NoyaValueOracle._getValue` **NOT** in the Validated Findings table.

## Idempotency
Re-running `--ingest-results` produced a byte-identical `value_provenance_advisory_results.json` (`diff` clean).

## Restore
noya `value_provenance_advisory_results.json` restored to its prior `ran:false` state; the P140-created
`value_provenance_manual_results/`, `value_provenance_ingestion_report.json`, and `review_gate.md` removed; noya
`session.json` restored; `output/` symlink restored to `quantamm-2024-04-eval`'s successor `quantamm-2024-12-eval`
(the working audit at session start). The `agent_policy.json active_audit` field is a vestigial/decoupled value
(`flare-network-2026-05`, not a registry audit; the symlink, not this field, drives `audit_context`) and was left
unchanged.

## Interpretation
The loop ingests + renders correctly end-to-end; 1 of 2 noya jobs completed (the other honestly left pending,
not fabricated) → **ACCEPT_PARTIAL_COMPLETION_LOOP**. The mechanism itself is fully functional; "partial" reflects
the measurement, not a defect.
