# P204 — integrity checks

## Production hashes byte-identical START == END (md5 first-8)
| artifact | START | END | ok |
|---|---|---|---|
| `prompts/deep_trace.md` | ef93a6c2 | ef93a6c2 | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | 5d2a97f9 | 5d2a97f9 | ✓ |
| `scripts/eval_locus_resolver.py` | 3b0b2c02 | 3b0b2c02 | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | e23c5bc9 | e23c5bc9 | ✓ |
| decent in-scope source tree | 623aedd6 | 623aedd6 | ✓ |
| P202 FREEZE1 / FREEZE2 | 54abf9ca / 90cf2a4f | 54abf9ca / 90cf2a4f | ✓ |
| P203 v2 regrade | e2100588 | e2100588 | ✓ |

No production prompt/checker/router/ledger/detector/severity edit; no `deep_trace.md` patch; no gate wired; no
submit/route/promote/demote. **Production decent contracts byte-identical** — the harness imports a byte-identical
**copy** in `pocs/realsrc/` (verified equal); production `audits/decent-.../contracts` untouched.

## Harness isolation & validity
- All harness/build artifacts live ONLY under `documentation/research/assisted_mode/p204_l3_magnitude_standard/pocs/`
  (`foundry.toml`, `src/mocks/`, `test/`, `realsrc/`, `out/`, `cache/`, `run_log.txt`).
- Only **external dependencies** mocked (LayerZero `OFTV2` base, solmate `Owned`, forge-std `IERC20`,
  `@uniswap IV3SwapRouter`); the **vulnerable logic is the real decent code**.
- 5/5 tests pass (`pocs/run_log.txt`): H-01 (2) + M-03 (2) + decent-06 (1). `fabrication_rate=0` — every L3 verdict
  is backed by a real run log, except decent-12 which is an explicitly documented source-valid-setup obstacle
  (NEEDS_HARNESS), not a fabricated result.

## Standard-before-results (anti-fit)
The L3 pass/fail criteria were pre-specified in the approved P204 brief and encoded as harness assertions before
result interpretation. Custody assumptions are stated explicitly in `M03_NEGATIVE_CONTROL_POC.md` / `FAILURE_CASES.md`.

## Symlink
`output -> audits/quantamm-2024-12-eval/output` — intact. All P204 JSON valid.

## Decision
`L3_STANDARD_PROMISING` — H-01 HIGH via executed material mint; M-03 + decent-06 demoted (no material theft under
honest custody); decent-12 NEEDS_HARNESS (source obstacle). HIGH bucket 6→1, 0 genuine-High loss — first clean
two-sided separation on decent.

## Deliverables
`P204_PLAN.md` · `INTEGRITY_PRECHECK.md` · `L3_HIGH_STANDARD.md` · `HARNESS_TARGET_MATRIX.md` ·
`H01_POSITIVE_CONTROL_POC.md` · `M03_NEGATIVE_CONTROL_POC.md` · `FALSE_HIGH_CONTROLS.md` · `L3_SCORECARD.md` ·
`FAILURE_CASES.md` · `P204_RECOMMENDATION.md` · `metrics.json` · `integrity_checks.md` + `pocs/` (foundry project,
3 `*.t.sol`, mocks, `realsrc/` byte-identical copy, `run_log.txt`).
