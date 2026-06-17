# P220 — Test results

## Foundry harnesses (executed L3 evidence) — `pocs/p220/`
| Suite | Command | Result | Log |
|-------|---------|--------|-----|
| ZETA04 | `forge test --match-contract ZETA04 -vv` | **3/3 PASS** | logs/ZETA04_run.log |
| ZETA10 | `forge test --match-contract ZETA10 -vv` | **2/2 PASS** | logs/ZETA10_run.log |
| ZETA11 | `forge test --match-contract ZETA11 -vv` | **2/2 PASS** | logs/ZETA11_run.log |
| all | `forge test -vv` | **7/7 PASS** | logs/ALL_run.log |

Toolchain: forge 1.5.1 / solc 0.8.7. Compiled real unmodified Zeta sources (`realsrc/`) + authentic OZ 4.8.1 +
Uniswap v3 interfaces (`vendor/`). Only warning: pre-existing `hasZetaLiquidity` state-mutability hint in the real
Trident source (not introduced by P220).

## Python tests
- New: `tests/research/test_p220_l3_harness_ingestion.py` (14 tests) — schema validity, artifact-backed PoC fields,
  card rendering, NEEDS_HARNESS stays explicit, decide() calibration, safety preserved.
- Edited: `tests/research/test_evidence_extraction.py` — the stale ZETA-04 `NEEDS_HARNESS` assertion (ZETA-04 was
  executed in P220) repointed to ZETA-05 (still NEEDS_HARNESS).
- Fast subset (`test_p220_l3_harness_ingestion + test_evidence_extraction`): **26/26 PASS** (70s).
- **Full research regression (`tests/research/`): 231 passed in 732s (0 failed).**

## Pipeline
- `run_hunt_sync_hook.py` (sync + completion guard `--strict`): exit **0**, guard **PASS**
  (failures/warnings/reader/card all empty, 12 records, all_safety_ok true).
