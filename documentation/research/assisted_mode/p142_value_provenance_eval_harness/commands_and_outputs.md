# P142 — Commands & Outputs

## Commands
```bash
# one-shot: seed -> ingest -> scorecard --append
python scripts/research/value_provenance_eval_harness.py all

# or step-by-step
python scripts/research/value_provenance_eval_harness.py seed --all
python scripts/research/value_provenance_eval_harness.py ingest --all
python scripts/research/value_provenance_eval_harness.py scorecard --append

# single architecture
python scripts/research/value_provenance_eval_harness.py seed --arch blackhole
python scripts/research/value_provenance_eval_harness.py ingest --arch blackhole
```

## Outputs (under `output_research/value_provenance_eval/`)
```
<arch>/value_provenance_advisory_results.json     # the eval_only_manual_queue (pending → completed)
<arch>/value_provenance_ingestion_report.json     # accepted/rejected/unmatched + refused_no_provenance
scorecard.json                                    # per-arch + totals + runs[] time-series
scorecard.md                                      # human-readable table
```
All carry the four research flags + `routing_allowed:false`. Nothing is written under any audit `output/` or
`review_gate.md`.

## Live run result (this phase)
```
[all] totals={'queued': 11, 'completed': 11, 'finding': 3, 'likely_exploitable': 0, 'needs_human': 1,
      'strong_clear': 7, 'error': 0, 'clean_strong_clear': 6, 'clean_false_finding': 0, 'buggy': 5, 'clean': 6,
      'buggy_useful': 4, 'buggy_strict': 3, 'rejected': 0, 'useful_recall': 0.8, 'strict_recall': 0.6,
      'clean_false_finding_rate': 0.0} · clean_FP_rate=0.0
```

## Verification
- `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → **empty** (UN-WIRED).
- `tests/research/test_value_provenance_eval_harness.py` → **14 passed**.
- Full suite **1651 passed** (1637 + 14) / 2 pre-existing deep_solidity snapshot fails / 4 skipped.
- `bash -n run_pipeline.sh` OK; `rank_signal_probe --self-test` OK; `output/` symlink unchanged
  (`quantamm-2024-12-eval`); `agent_policy.json` unchanged.
