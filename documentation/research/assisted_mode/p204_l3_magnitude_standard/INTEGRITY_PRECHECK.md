# P204 — integrity precheck

## START hashes (md5sum first-8)
| artifact | START | expected | match |
|---|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` | ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | `e23c5bc9` | ✓ |
| decent in-scope source tree (concat) | `623aedd6` | `623aedd6` | ✓ |
| P202 FREEZE1 raw outputs | `54abf9ca` | `54abf9ca` | ✓ |
| P202 FREEZE2 v1 calibration | `90cf2a4f` | `90cf2a4f` | ✓ |
| P203 v2 regrade | `e2100588` | `e2100588` | ✓ |

## Toolchain (read-only check)
`forge 1.5.1`, `solc 0.8.24` (forge auto-selected 0.8.30 for ^0.8.13), `anvil` present → harnesses run.

## Harness isolation
All harness files are NEW and isolated under
`documentation/research/assisted_mode/p204_l3_magnitude_standard/pocs/` (self-contained Foundry project:
`foundry.toml`, `src/mocks/`, `test/`, `realsrc/`, `out/`, `cache/`). **No production contract edited.** The real
decent source is imported by a **byte-identical copy** in `pocs/realsrc/` (verified equal to the originals;
production `audits/decent-.../contracts` untouched — tree hash `623aedd6` unchanged START==END). Only **external
dependencies** are mocked (`src/mocks/`: LayerZero `OFTV2` base, solmate `Owned`, `forge-std/interfaces/IERC20`,
`@uniswap` `IV3SwapRouter`). The vulnerable logic is the **real decent code**.

## Note on deliverable ordering (transparency)
The L3 standard's pass/fail criteria were **pre-specified in the approved P204 brief** (and encoded directly as
assertions in the harness `.t.sol` files) before run results were interpreted, so there is no post-hoc fitting.
`L3_HIGH_STANDARD.md` documents that pre-given standard.

## Symlink
`output -> audits/quantamm-2024-12-eval/output` — intact.

## END re-check
Recorded in `integrity_checks.md` — START==END required for production artifacts + decent source + P202/P203 freezes.
