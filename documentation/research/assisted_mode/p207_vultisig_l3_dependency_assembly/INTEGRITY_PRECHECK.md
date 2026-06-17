# P207 — integrity precheck (START)

## START production hashes (md5 first-8) — must be byte-identical at END
| artifact | hash |
|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` |
| `../hermes/memory/events.jsonl` (ledger) | `fc446040` |
| Vultisig src tree (`audits/vultisig-2024-06-holdout/contracts/src`, all `.sol`) | `d9489e47` |

## Answer-key state
- Vultisig `_sealed_answer_key` was opened READ-ONLY in P205 (post-FREEZE-1 mapping). P207 **reuses P205's mapped
  target classes** (H-01 positive, M-03 negative) — **no new blind run**, no re-open required for target selection.
- P205 FREEZE-1 raw-outputs hash `fa1afe1b` (unchanged reference).

## Scope confirmation
- Original Vultisig source untouched (verified byte-identical to `realsrc/` copy throughout).
- Deps + harnesses isolated under `documentation/research/assisted_mode/p207_vultisig_l3_dependency_assembly/pocs/p207/`.
- No production prompt/checker/router/ledger/detector/dashboard change; no L3 wiring.
