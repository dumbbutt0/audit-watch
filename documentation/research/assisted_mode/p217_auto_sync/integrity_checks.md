# P217 — INTEGRITY CHECKS (END)

## Production hashes START → END (md5 first-8)
| File | START | END | status |
|------|-------|-----|--------|
| `scripts/dashboard_sync.py` | 26bd7ee0 | 26bd7ee0 | SAME |
| `scripts/build_synced_findings.py` | a7853775 | **2fb00b0e** | CHANGED (→ thin shim over the wrapper) |
| `scripts/funnel.py` | d9f09981 | d9f09981 | SAME |
| `scripts/finding_detail.py` | f12aa8d3 | f12aa8d3 | SAME |
| `scripts/findings_overview.py` | 5c6cccb5 | 5c6cccb5 | SAME |
| `scripts/dashboard.py` | 197ac4d5 | 197ac4d5 | SAME |
| `scripts/submission_readiness_review.py` | e4960878 | e4960878 | SAME |
| `scripts/final_submission_pack.py` | 57cba16d | 57cba16d | SAME |
| `documentation/research/funnel/funnel_records.json` | b3278eed | b3278eed | SAME |
| `documentation/research/funnel/synced_findings.generated.json` | eb359941 | **d578cd87** | CHANGED (regenerated, richer; same 12 ids) |
| `config/runtime_policy.json` | bea43487 | bea43487 | SAME (`api_free:true`) |
| `output_research/option_a_campaign/ledger.jsonl` | e23c5bc9 | e23c5bc9 | SAME |
| `prompts/deep_trace.md` | ef93a6c2 | ef93a6c2 | SAME (forbidden) |
| `scripts/min_confirm_gate.py` | 41dd3c96 | 41dd3c96 | SAME (forbidden) |
| `scripts/confirm_gate.py` | 4fadfc5f | 4fadfc5f | SAME (forbidden) |

Only the shim + the generated mirror changed. **No production-code edit was needed** beyond the shim — the P216
contract already supported rich inline fields. All forbidden files byte-identical.

## Safety
- No external submission/route/promote; wrapper is research-only, read-only on shared inputs; the only file it writes is
  the generated mirror (backup-first, idempotent).
- Every emitted record: `research_only/review_only:true`, `routes_in_production/routing_allowed/submission_ready:false`,
  `no_submit_controls:true`, `browser_computes_severity:false`, `canonical_submission_ready_source` present,
  `human_review_required:true` (enforced by `validate_synced` + `safety_ok`; `--strict` aborts on violation).
- Severity recorded-or-HUMAN_PENDING; no invented fields; unknowns explicit.

## Backups / reversibility
`synced_findings.generated.json.bak.<ts>` written before each generate. Pre-P217 mirror state recoverable from backup
or by `--replace-phase-records` with empty input. `funnel_records.json` untouched.

## Tests / JSON
`tests/research/test_sync_hunt_findings.py` 14/14; full regression (P216+P217+funnel+overview+detail) — see TEST_RESULTS.
`metrics.json` valid; `synced_findings.generated.json` valid JSON (schema synced-1, 12 records); fabrication 0.
