# P140 — Implementation Summary

Additive only; 5 files. No detector / severity / submission / gate-logic change. No non-interactive runner. No
external API. No new detector. P130–P139 preserved.

## 1. `scripts/run_value_provenance_advisories.py` (+`--ingest-results`)
- New vocabularies: `ALLOWED_DECISIONS`, `ALLOWED_CONFIDENCE`, `RECOMMENDED_NEXT`.
- `DEFAULT_CFG` + 3 keys: `auto_run_value_provenance_manual_results_dir`,
  `auto_run_value_provenance_hide_strong_clear`, `auto_run_value_provenance_ingest_on_review_gate`.
- `_validate_completion(art) -> (ok, reason)` — quarantines unsafe/forbidden/invalid artifacts.
- `_load_manual_results(dir) -> list` — reads `*.json`; missing dir → `[]`; per-file malformed → quarantine
  marker (never raises).
- `ingest_results(report, manual_results, cfg) -> (updated_report, ingestion_report)` — **pure**, deterministic,
  idempotent. Matches by `job_id==advisory_id`; sets `auto_run_status=completed` (or `failed` for `error`); copies
  decision/confidence/summaries/next-step/`completed_at` from the artifact; **forces the advisory triplet**;
  records `accepted` / `rejected{file,job_id,reason}` / `unmatched`; leaves unmatched + artifact-less pending jobs
  untouched.
- `_run_ingest(out_dir, mr_dir, cfg, quiet)` — I/O wrapper; writes updated
  `value_provenance_advisory_results.json` + `value_provenance_ingestion_report.json`.
- `main()` — new `--ingest-results` branch, wrapped in its own fail-open try/except (never blocks).

## 2. `scripts/generate_review_gate.py` (`_value_provenance_section`)
- Table extended to `| Status | Location | Decision | Confidence | Next step | Mechanism | Job |`.
- `finding`/`likely_exploitable` → rendered as **"<decision> — NOT confirmed"**; `strong_clear` → **"strong_clear
  (cleared advisory context)"**; honours `auto_run_value_provenance_hide_strong_clear` (hides cleared rows; section
  disappears if all hidden).
- Unchanged guarantees: never added to `findings`; Validated Findings + confirmed count unaffected; robust to
  missing/malformed/empty.

## 3. `config/agent_policy.json` (`value_provenance_auto_run`)
+3 keys (defaults: dir `output/value_provenance_manual_results`, hide_strong_clear `false`,
ingest_on_review_gate `true`) + updated block description. Master flag / `mode=off` still disables all.

## 4. `run_pipeline.sh`
After the P139 build call and before `generate_review_gate.py`, in both `full` and `review-gate`:
`run_value_provenance_advisories.py --ingest-results 2>/dev/null || true` (non-blocking; folds any on-disk manual
results in before rendering).

## 5. `tests/mechanism_advisory/test_value_provenance_completion.py` (new, 16 tests)
Covers the 13 planned cases + error→failed, forbidden-field quarantine, and an end-to-end `main(--ingest-results)`.
