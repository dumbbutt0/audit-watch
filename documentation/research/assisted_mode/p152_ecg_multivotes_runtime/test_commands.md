# P152 — Test Commands

## Runtime PoC
```bash
cd audits/ecg-2023-12-holdout/pocs/p152
forge test -vv
```
Restore build deps if `lib/` was cleaned:
```bash
git clone --depth 1 --branch v1.9.4 https://github.com/foundry-rs/forge-std lib/forge-std
git clone --depth 1 --branch v4.9.6 https://github.com/OpenZeppelin/openzeppelin-contracts lib/openzeppelin-contracts
```

Result: `3 passed` — real guarded transfer decrements delegatee votes 1000e18→0 (suspicion refuted); vulnerable
reference retains 1000e18; control stable.

## Panel
```bash
python scripts/research/value_provenance_eval_harness.py all
```
- panel summary: `{rows: 15, runtime_only: 4, by_status: {runtime_confirmed: 4, runtime_refuted: 2, not_run: 9}}`.
- new runtime-only row `H4-ecg-multivotes-accounting`: `runtime_refuted` / `duplicate_unknown` / `runtime_only:true`
  / routing+submission false; `conversion.outcome = runtime_refuted`.
- prompt `totals` **byte-for-byte == P138 baseline** (finding 3 / needs_human 1 / strong_clear 7; useful_recall
  0.80; clean_FP 0.0).

## Verification
- `python -m pytest tests/research/test_value_provenance_eval_harness.py -q` → **36 passed** (33 + 3 new).
- full `pytest -q` → **1673 passed** (1670 + 3) / 2 pre-existing deep_solidity snapshot fails / 4 skipped.
- `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty (UN-WIRED).
- `ERC20MultiVotes.sol` byte-identical (18475 bytes); `output/` symlink still `quantamm-2024-12-eval`.
