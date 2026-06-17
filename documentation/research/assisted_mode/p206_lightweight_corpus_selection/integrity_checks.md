# P206 — integrity checks (START == END)

## Production artifacts — byte-identical START==END (read-only all phase)
| artifact | START | END |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` ✓ |
| `../hermes/memory/events.jsonl` (ledger) | `fc446040` | `fc446040` ✓ |

## Seals
- munchables-2024-05 / pooltogether-2024-03 answer keys: **still sealed** at END ✓ (read read-only during screening).
- Orchestrator exposure: severity **counts** + source metadata only; finding bodies/titles read only by firewall
  subagents (not the orchestrator) — except the run-2 prose leak below.

## Firewall discipline
- High-viability classification via **JSON-only firewall subagent**, 2 runs:
  - Run 1 (`af0674e3...`): benign prose preamble (no titles/loci) → **discarded**, rerun.
  - Run 2 (`ad3242...`): prose preamble **leaked mechanism hints** → **discarded**; **JSON persisted** (agrees with
    run 1). **Orchestrator contamination logged** (`SCREENING_OUTPUTS.json.firewall_contamination_caveat`) →
    mitigation carried to P207 (fresh key-blind blind subagents + post-freeze scoring, as P202/P205).
- Process fix recorded: enforce first-char `{` / last-char `}`; void on any preamble.

## Harness smoke test
- munchables `contracts/src` (excl test/mock/rng) compiled **successfully** (94 files, solc 0.8.25, local OZ v5) — see
  `smoke_build_result.txt` / `smoke_foundry.toml`. Throwaway build dir trimmed (no heavy source duplication).
- No exploit PoC built; non-mutating.

## Decision
`FALLBACK_TO_VULTISIG_DEPENDENCY_ASSEMBLY`. Corpus-selection phase; no production change; research-only, un-wired.
`fabrication_rate = 0` (every classification backed by a firewall-subagent JSON run or a compile log; compile result
is an objective forge output).
