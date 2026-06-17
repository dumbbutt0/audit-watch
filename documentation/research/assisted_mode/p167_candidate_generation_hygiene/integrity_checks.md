# P167 integrity checks

| Artifact | Baseline | Post-P167 | Result |
|---|---|---|---|
| campaign ledger — existing 6 rows (`head -6`) | `412a139c…` | `412a139c…` | **byte-identical** (H11–H13 appended as rows 7–9; no rewrite/backfill) |
| campaign ledger row count | 6 | 9 | append-only +3 (H11, H12, H13) |
| prediction_log.jsonl lines | 1 | 4 | append-only +3 (H11–H13 predictions) |
| runtime sidecar | `491da8c1…` | `491da8c1…` | **byte-identical** (H11–H13 not_run → no sidecar rows) |
| frozen corpus | `60089ff5…` | `60089ff5…` | **byte-identical** |
| readiness file | `ff8243c4…` | `ff8243c4…` | **byte-identical** |
| production `generate_scope_inventory.py` | `9088a59a…` | `9088a59a…` | **byte-identical** (not modified) |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- Part A (hygiene tooling) + Part B (HYGIENE.md) are independent of the Part C (H11–H13) runs; all three were
  recorded `SOURCE_REFUTED_NO_HARNESS` (no forced harness — independence guardrail honored).
- `sandbox_check.py` CLEAN before reading each candidate source. No harness built → no PoC dir / Foundry lib.
- Hygiene gate proven: `scan_signals(revert-lend, "originalOwner")` → `[]` (H10 would be filtered).
- Campaign tool stays **un-wired**: `grep option_a_campaign|p167 run_pipeline.sh config/agent_policy.json` → empty.
- All H11–H13 rows carry `candidate_signal_source=protocol_src`; none set `submission_ready`/`routing_allowed`;
  `fabrication_rate = 0/9`.
- No detector / taxonomy / routing / severity / submission-policy / prompt / corpus / sidecar-schema /
  production change.
