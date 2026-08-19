# Submission packs — 0xMarkets (0xMarkets_contract-main, commit e94daee6) — audit 2026-06-23/24

13 finding folders (12 real + 1 merged/rejected/info). Each `<ID>/` is self-contained: `report.md` + `sources/` (full vulnerable files). The permissionless PoC bugs additionally have `SUBMISSION.md` (bounty-ready) + `poc/` (test + run output).

See **`INDEX.md`** for the full table grouped by disposition (real / merged duplicate / rejected honest-negative / info).

Every `report.md` carries a disposition banner — merged duplicates and rejected honest-negatives are kept for traceability and must NOT be submitted.

## Reproduce the PoC (Hardhat integration)
```bash
cd ~/clones/0xMarkets_contract-main
npm install --legacy-peer-deps --ignore-scripts
node_modules/.bin/hardhat test test/guardian/PoC_LeverageLadderBypass.ts  # POS-001 (Medium)
```
In-pack copy of the test lives under `POS-001/poc/` (with `run_output.txt`).

