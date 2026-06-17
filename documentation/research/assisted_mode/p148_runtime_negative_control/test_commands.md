# P148 — Test Commands

## Runtime PoC
```bash
cd audits/velodrome-2022-05-bench/pocs/p148
forge test -vv
```
Restore build deps if `lib/` was cleaned:
```bash
git clone --depth 1 --branch v1.9.4 https://github.com/foundry-rs/forge-std lib/forge-std
```
(No OpenZeppelin — `RewardsDistributor` imports only local `Math`/`IERC20`/`IVotingEscrow`.)

Result: `3 passed` — suspected divergence does not occur (external recipient 0; both `deposit_for` their own
tokenId 1e18), siblings identical, control credits the right tokenId.

## Panel
```bash
python scripts/research/value_provenance_eval_harness.py runtime-panel
python scripts/research/value_provenance_eval_harness.py all
```
- `runtime_panel.json` summary: `{rows: 13, runtime_only: 2, by_status: {runtime_confirmed: 3, not_run: 9,
  runtime_refuted: 1}}`.
- New runtime-only row `H2-velodrome-rewardsdist-parity`: `runtime_refuted` / `duplicate_unknown` /
  `runtime_only: true` / routing+submission false.
- Prompt `totals` **byte-for-byte == P138 baseline** (finding 3 / needs_human 1 / strong_clear 7;
  useful_recall 0.80; clean_FP 0.0).

## Verification
- `python -m pytest tests/research/test_value_provenance_eval_harness.py -q` → **27 passed** (24 + 3 new).
- full `pytest -q` → **1664 passed** (1661 + 3) / 2 pre-existing deep_solidity snapshot fails / 4 skipped.
- `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty (UN-WIRED).
- `bash -n run_pipeline.sh` OK; `output/` symlink still `quantamm-2024-12-eval`.
