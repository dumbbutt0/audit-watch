# P206 — integrity precheck (START)

Corpus-selection phase. No production mutation; read-only screening + a non-mutating compile smoke test only.

## START production hashes (md5 first-8) — must be byte-identical at END
| artifact | hash |
|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` |
| `../hermes/memory/events.jsonl` (ledger) | `fc446040` |

## Seals (all candidate answer keys remain sealed before screening)
- `munchables-2024-05-holdout/_sealed_answer_key` — SEALED ✓
- `pooltogether-2024-03-holdout/_sealed_answer_key` — SEALED ✓
- `badger-2024-06-holdout/_sealed_answer_key` — SEALED ✓
- `kleidi-2024-10-holdout/_sealed_answer_key` — SEALED ✓
- (decent/vultisig/zetachain/centrifuge/predy keys not re-touched; already-used corpora.)

## Firewall posture
- Orchestrator exposure limited to **severity counts** (`# High/Medium Risk Findings (N)` summary headers) and
  **source-tree metadata** (file names, pragmas, import roots). No finding bodies/titles read by the orchestrator.
- Contract-level High **category** classification routed to a **JSON-only firewall subagent** (step 4): no prose
  preamble, no verbatim titles, no loci. Leakage → discard + rerun stricter.
- Smoke-test artifacts isolated under this p206 dir; production audit sources imported read-only / via byte-identical
  throwaway copies, never edited.

Scope guardrails (no L3 wiring, no prompt/checker/router/ledger/detector/dashboard change, no submit/route/promote/
demote, no full PoCs) carried from the approved plan.
