# P216 — INTEGRITY CHECKS (END)

## Production hashes START → END (md5 first-8)
| File | START | END | status |
|------|-------|-----|--------|
| `scripts/dashboard.py` | 197ac4d5 | 197ac4d5 | SAME |
| `scripts/findings_overview.py` | 5c6cccb5 | 5c6cccb5 | SAME |
| `scripts/funnel.py` | 14f1e1c7 | **d9f09981** | CHANGED (additive `load_records` mirror merge, gated to the implicit default-path call only) |
| `scripts/candidate_detail.py` | da925496 | da925496 | SAME |
| `scripts/finding_detail.py` | 0c05f470 | **f12aa8d3** | CHANGED (additive full-record resolve + inline-section preference in `_funnel_detail`/`build_verifier_evidence`) |
| `scripts/submission_readiness_review.py` | e4960878 | e4960878 | SAME |
| `scripts/final_submission_pack.py` | 57cba16d | 57cba16d | SAME |
| `documentation/research/funnel/funnel_records.json` | 99f5a6a7 | **b3278eed** | CHANGED (one-time migration → pre-P215 8 records) |
| `config/runtime_policy.json` | bea43487 | bea43487 | SAME (`api_free:true`) |
| `output_research/option_a_campaign/ledger.jsonl` | e23c5bc9 | e23c5bc9 | SAME |
| `prompts/deep_trace.md` | ef93a6c2 | ef93a6c2 | SAME (forbidden) |
| `scripts/min_confirm_gate.py` | 41dd3c96 | 41dd3c96 | SAME (forbidden) |
| `scripts/confirm_gate.py` | 4fadfc5f | 4fadfc5f | SAME (forbidden) |

Only the 3 intended files changed; all 3 forbidden files + all other tracked production files byte-identical.

## Safety
- No external submission / route / promote; `dashboard_sync` + generator are research-only, read-only-on-shared-files.
- Canonical `submission_ready` never set true; `routing_allowed` never true; `browser_computes_severity:false`.
- No dashboard submit/promote controls added (HTML unchanged; test enforces).
- Both code edits are additive + read-only (no severity/routing/gate logic touched); `_sev_or_status` unchanged.
- Generator: backup-before-write, idempotent, schema-validated, reversible (delete the mirror).

## Backups
`funnel_records.json.bak.20260607T050647Z` (pre-P215, 8) · `funnel_records.json.bak.pre-p216.<ts>` (20-record state) ·
`synced_findings.generated.json.bak.<ts>` (generator backups).

## JSON / tests
`synced_findings.generated.json` valid (schema synced-1, 12 records); `metrics.json` valid;
`tests/research/test_dashboard_sync.py` 16/16 pass; fabrication 0; `api_free=true` unchanged.
