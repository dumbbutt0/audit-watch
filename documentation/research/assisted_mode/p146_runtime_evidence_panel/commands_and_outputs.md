# P146 — Commands & Outputs

## Commands
```bash
# standalone panel
python scripts/research/value_provenance_eval_harness.py runtime-panel
# full run (seed -> ingest -> scorecard, which now also emits the panel)
python scripts/research/value_provenance_eval_harness.py all
```

## Outputs (under `output_research/value_provenance_eval/`)
- `scorecard.json` — now contains `per_arch` / `totals` / `runs` (prompt metrics, **unchanged**) **plus** an
  additive `runtime_panel` key.
- `runtime_panel.json` — standalone panel (11 rows, `summary`, `integrity`, four research flags).
- `scorecard.md` — gains a "Runtime Evidence Panel" section; `runtime_panel.md` standalone.

## Live result
```
[all] totals={'queued': 11,'completed': 11,'finding': 3,'likely_exploitable': 0,'needs_human': 1,
      'strong_clear': 7,'error': 0,'clean_strong_clear': 6,'clean_false_finding': 0,'buggy': 5,'clean': 6,
      'buggy_useful': 4,'buggy_strict': 3,'rejected': 0,'useful_recall': 0.8,'strict_recall': 0.6,
      'clean_false_finding_rate': 0.0}                         <-- value-for-value == P142 baseline

runtime_panel: summary={'rows': 11, 'by_status': {'runtime_confirmed': 2, 'not_run': 9}}
  B1 noya       runtime_confirmed high duplicate_known routing=False sub=False
  B5 blackhole  runtime_confirmed high duplicate_known routing=False sub=False
  (9 others: not_run / none)
integrity={'supplemental_only': True,'production_source_modified': False,'routing_allowed_all_false': True,
           'submission_ready_all_false': True,'prompt_metrics_mutated_by_panel': False,'backfilled': ['B1','B5']}
```

## Verification
- `python -m pytest tests/research/test_value_provenance_eval_harness.py -q` → **20 passed** (14 + 6 new).
- full `pytest -q` → **1657 passed** (1651 + 6) / 2 pre-existing deep_solidity snapshot fails / 4 skipped.
- `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty (UN-WIRED).
- `bash -n run_pipeline.sh` OK; `rank_signal_probe --self-test` OK; `output/` symlink still `quantamm-2024-12-eval`.
