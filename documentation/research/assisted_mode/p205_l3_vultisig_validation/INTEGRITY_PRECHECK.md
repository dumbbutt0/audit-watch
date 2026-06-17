# P205 — integrity precheck

## START hashes (md5sum first-8)
| artifact | START | expected | match |
|---|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` | ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | `e23c5bc9` | ✓ |
| vultisig in-scope `src/` tree (concat) | `d9489e47` | `d9489e47` | ✓ |

## Toolchain
`forge 1.5.1`, `solc 0.7.6`+ available; network/`forge install` available (fallback for vendored deps). vultisig is
**solc =0.7.6** (OZ v3.4-era + Uniswap v3-core 0.7.6).

## Seal
`audits/vultisig-2024-06-holdout/_sealed_answer_key/report.md` present, unopened at precheck. Count-only viability
(Step 2) reads section headers only; full read only at the post-FREEZE-1 mapping step.

## Harness isolation
All harness/build artifacts isolated under `documentation/research/assisted_mode/p205_l3_vultisig_validation/pocs/`.
Real vultisig source imported via a byte-identical copy (`pocs/realsrc/`, hash-verified); production
`audits/vultisig-.../contracts` untouched (tree `d9489e47` START==END). Only external deps (OZ, Uniswap v3-core,
faithful V3 pool) provided as real-vendored/mocked dependencies — never the vulnerable logic.

## Contamination note
Orchestrator was PCS-exposed to vultisig High hints. As in P204, L3 results are objective EVM executions; target
selection + harness setup pre-registered + source-justified; blind subagents fresh/key-blind. Recorded.

## Symlink
`output -> audits/quantamm-2024-12-eval/output` — intact.

## END re-check
`integrity_checks.md` at close — START==END required for production artifacts + vultisig source tree.
