# Submission packs — Cartha Vaults (cartha-vaults-main, commit 4c51f2a8) — audit 2026-06-23/24

32 finding folders (22 real + 10 merged/rejected/info). Each `<ID>/` is self-contained: `report.md` + `sources/` (full vulnerable files). The permissionless PoC bugs additionally have `SUBMISSION.md` (bounty-ready) + `poc/` (test + run output).

See **`INDEX.md`** for the full table grouped by disposition (real / merged duplicate / rejected honest-negative / info).

Every `report.md` carries a disposition banner — merged duplicates and rejected honest-negatives are kept for traceability and must NOT be submitted.

## Reproduce the PoCs (Foundry)
```bash
cd ~/clones/cartha-vaults-main
forge test --match-path 'test/poc/PoC_GmDecimalMismatch.t.sol' -vv   # CARTHA-SEAM-001 (Critical)
forge test --match-path 'test/poc/PoC_AsyncWindowDilution.t.sol' -vv # DT-001 (High)
```
In-pack copies of the tests live under `CARTHA-SEAM-001/poc/` and `DT-001/poc/` (with `run_output.txt`).

