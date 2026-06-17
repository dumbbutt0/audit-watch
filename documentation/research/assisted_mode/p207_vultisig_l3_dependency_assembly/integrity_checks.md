# P207 — integrity checks (START == END)

## Production artifacts — byte-identical START==END (read-only all phase)
| artifact | START | END |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` ✓ |
| `../hermes/memory/events.jsonl` (ledger) | `fc446040` | `fc446040` ✓ |
| Vultisig src tree | `d9489e47` | `d9489e47` ✓ |

## Isolation & source integrity
- Vultisig `_sealed_answer_key` still sealed at END; not re-opened (P205 mapping reused; no new blind run).
- `pocs/p207/realsrc/src` **byte-identical** to production Vultisig src (`diff -rq` clean; `d9489e47`).
- Original Vultisig source NOT edited. Deps confined to `pocs/p207/lib/` (OZ v3.4.0 + v3-core v1.0.0; `.git` stripped).
- No production prompt/checker/router/ledger/detector/dashboard change; no L3 wiring.

## Reproducibility
- solc 0.7.6 / forge 1.5.1. `forge build` → 58 files, success, 0 source edits. `forge test -vv` → 3/3 pass
  (`pocs/p207/run_log.txt`). Build artifacts (`out/`, `cache/`) trimmed; regenerable via `forge test`.
- Every L3 verdict backed by a forge run log; `fabrication_rate = 0`.

## Decision
`L3_STANDARD_VALIDATED_SECOND_CORPUS` — converts P205 PARTIAL → VALIDATED. Research-only, un-wired.
