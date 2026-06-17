# P140 — Tests & Commands

## New test file
`tests/mechanism_advisory/test_value_provenance_completion.py` — 16 tests (13 planned + 3 extra), no
protocol-specific strings.

| # | Test | Proves |
|---|---|---|
| 1 | `test_pending_stays_pending_no_artifact` | pending stays pending when no artifact |
| 2 | `test_valid_completion_to_completed` | valid finding → completed; triplet preserved |
| 3 | `test_review_gate_strong_clear_cleared` | strong_clear renders as cleared advisory context |
| 4 | `test_review_gate_finding_not_confirmed` | finding renders "NOT confirmed"; not in Validated Findings |
| 5 | `test_submission_ready_quarantined` | `submission_ready:true` quarantined, job untouched |
| 6 | `test_advisory_only_false_quarantined` | `advisory_only:false` quarantined |
| 6b | `test_confirmed_and_severity_quarantined` | `confirmed:true` / bare `final_severity` quarantined; non-binding allowed |
| 7 | `test_malformed_no_block` | malformed artifact → rejected, no raise |
| 8 | `test_unmatched_no_mutation` | unmatched `job_id` → recorded, no mutation |
| 9 | (in #4) | completed result absent from Validated Findings |
| 10 | `test_review_gate_confirmed_count_unchanged` | confirmed count unchanged |
| 11 | `test_ingestion_report_counts` | accepted/rejected/unmatched/completed/pending counts accurate |
| 12 | `test_missing_results_dir_safe` | missing results dir → `[]` |
| 13 | `test_rerun_idempotent` | re-ingest yields identical entry |
| + | `test_error_decision_failed` | `error` decision → `failed` status |
| + | `test_review_gate_hide_strong_clear` | hide flag removes cleared rows / section |
| + | `test_main_ingest_end_to_end` | `main(--ingest-results)` writes both reports, fail-open |

## Commands
```bash
# focused
python -m pytest tests/mechanism_advisory/test_value_provenance_completion.py -q   # 16 passed
python -m pytest tests/mechanism_advisory/ -q                                       # 51 passed

# pipeline syntax + self-test
bash -n run_pipeline.sh                                                             # OK
python scripts/assisted/rank_signal_probe.py --self-test                           # SELF-TEST: OK

# operator loop
python scripts/run_value_provenance_advisories.py                 # build/queue (P139)
python scripts/run_value_provenance_advisories.py --ingest-results # ingest manual results (P140)
python scripts/generate_review_gate.py                            # re-render

# full suite
python -m pytest -q   # 1637 passed, 2 pre-existing deep_solidity snapshot fails, 4 skipped
```

## Result
1637 passed (1621 baseline + 16 new) / 2 pre-existing `deep_solidity` frozen-snapshot fails (output/ symlink
coupling, unrelated to P140) / 4 skipped. `bash -n` clean. self-test OK.
