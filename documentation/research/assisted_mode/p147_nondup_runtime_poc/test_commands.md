# P147 — Test Commands

## Runtime PoC
```bash
cd audits/centrifuge-2023-09-holdout/pocs/p147
forge test -vv
```
Restore build deps if `lib/` was cleaned:
```bash
git clone --depth 1 --branch v1.9.4 https://github.com/foundry-rs/forge-std lib/forge-std
```
(No OpenZeppelin — `UserEscrow` imports only local `Auth` + `SafeTransferLib`.)

Result: `4 passed` — vulnerable redirect to receiver (1000e18), corrected reverts, control pays destination,
repeat redirect (2000e18).

## Panel
```bash
python scripts/research/value_provenance_eval_harness.py runtime-panel   # standalone panel
python scripts/research/value_provenance_eval_harness.py all             # seed→ingest→scorecard (+panel)
```
- `runtime_panel.json` summary: `{rows: 12, runtime_only: 1, by_status: {runtime_confirmed: 3, not_run: 9}}`.
- New runtime-only row `H1-centrifuge-userescrow`: `runtime_confirmed` / high / `duplicate_unknown` /
  `runtime_only: true` / routing+submission false.
- Prompt `totals` **byte-for-byte == P138 baseline** (finding 3 / needs_human 1 / strong_clear 7;
  useful_recall 0.80; clean_FP 0.0).

## Verification
- `python -m pytest tests/research/test_value_provenance_eval_harness.py -q` → **24 passed** (20 + 4 new).
- full `pytest -q` → **1661 passed** (1657 + 4) / 2 pre-existing deep_solidity snapshot fails / 4 skipped.
- `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty (UN-WIRED).
- `bash -n run_pipeline.sh` OK; `output/` symlink still `quantamm-2024-12-eval`.
