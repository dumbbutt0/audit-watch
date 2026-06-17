# P150 — Test Commands

## Runtime PoC
```bash
cd audits/decent-2024-01-holdout/pocs/p150
forge test -vv
```
Restore build deps if `lib/` was cleaned:
```bash
git clone --depth 1 --branch v1.9.4 https://github.com/foundry-rs/forge-std lib/forge-std
git clone --depth 1 https://github.com/transmissions11/solmate lib/solmate
```

Result: `3 passed` — signer authorized 1e18 but real `collectFees` charged the unsigned 1000e18; corrected
reference reverts; matched control charges the signed amount.

## Panel
```bash
python scripts/research/value_provenance_eval_harness.py runtime-panel
python scripts/research/value_provenance_eval_harness.py all
```
- panel summary: `{rows: 14, runtime_only: 3, by_status: {runtime_confirmed: 4, runtime_refuted: 1, not_run: 9}}`.
- new runtime-only row `H3-decent-utbfeecollector-sigbind`: `runtime_confirmed` / `duplicate_unknown` /
  `runtime_only: true` / routing+submission false.
- prompt `totals` **byte-for-byte == P138 baseline** (finding 3 / needs_human 1 / strong_clear 7; useful_recall
  0.80; clean_FP 0.0).

## Verification
- `python -m pytest tests/research/test_value_provenance_eval_harness.py -q` → **31 passed** (29 + 2 new).
- full `pytest -q` → **1668 passed** (1666 + 2) / 2 pre-existing deep_solidity snapshot fails / 4 skipped.
- `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty (UN-WIRED).
- `bash -n run_pipeline.sh` OK; `UTBFeeCollector.sol` byte-identical (2629 bytes); `output/` symlink still
  `quantamm-2024-12-eval`.
