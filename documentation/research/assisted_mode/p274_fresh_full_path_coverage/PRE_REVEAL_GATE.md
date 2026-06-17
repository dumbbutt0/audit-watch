# P274 — PRE_REVEAL_GATE (Phase 9)

The full pre-reveal candidate + PoC set is **frozen + hashed BELOW before the answer key is opened** (Phase 10). No
finding titles / bodies / report tables / severity / award summaries were read up to this point. Status labels are
advisory only: `PRE_REVEAL_STRONG` / `PRE_REVEAL_PARTIAL_CANDIDATE` / `REFUTED` / `NEEDS_MORE_RUNTIME` — never
severity / reportable / submission / confirmed.

## Frozen pre-reveal set (sha256[:16])
| artifact | hash |
|---|---|
| outputs/selector_pairs.json | `f9379162dc616197` |
| outputs/selector_decisions.json | `cc1dddece1bcb245` |
| outputs/coverage_candidates.json | `cd6f9fb3f8bc5034` |
| outputs/coverage_decisions.json | `b00b6cc9128c3d5b` |
| outputs/triage_candidates.json | `ff16bb2df9cbb808` |
| outputs/triage_decisions.json | `391ed3f3d362a750` |
| RANKING_AND_COMPLETION.md | `f7b476c525e26f1a` |
| POC_INTENT.md | `1f7c1732bbda012a` |
| POC_RESULTS.md | `f29350e0718ff9df` |
| pocs/p274/gondi/test/P274_Distribute.t.sol | `425b6130896d9afd` |
| pocs/p274/gondi/test/P274_UserVault.t.sol | `ed5f25480ec5724f` |
| pocs/p274/gondi/test/P274_WithdrawalQueue.t.sol | `5e28f7d03d2c634b` |
| pocs/p274/gondi/run_output.txt | `27b7f8d4152b57f1` |
| BASE_AND_HARNESS_FREEZE.md (Phase 1) | (manifest/harness hashes therein) |

## Pre-reveal candidate ledger (advisory)
| id | class | status | PoC |
|---|---|---|---|
| M1 `distribute` permissionless spoofed `loanLiquidation` callback | ACCOUNTING + ACCESS | **PRE_REVEAL_STRONG** (reachability) / PARTIAL (economic) | PASS + control PASS |
| M3 `burnAndWithdraw` strands unlisted assets (burn-before-withdraw, no recovery) | STATE_MACHINE | **PRE_REVEAL_PARTIAL_CANDIDATE** | PASS |
| M2 WithdrawalQueue per-share rounding strands dust + ÷0 pre-mint | SHARE / DOS | **PRE_REVEAL_PARTIAL_CANDIDATE** | PASS x2 |
| M4 `offers` order validation | ORDER_VALIDATION | **NEEDS_MORE_RUNTIME** (no exact hypothesis) | — |

4 award classes carried into PoC; 3 runtime-proven mechanisms across 3 distinct classes; 1 class (ORDER) advanced only
to control-flow. No production authority, no severity, no submission state assigned.

**Gate sealed.** Phase 10 opens the answer key against this frozen set only.
