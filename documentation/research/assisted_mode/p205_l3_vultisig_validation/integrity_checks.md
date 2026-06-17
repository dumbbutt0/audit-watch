# P205 — integrity checks (START == END)

## Production artifacts — byte-identical START==END (read-only all phase)
| artifact | hash | status |
|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | unchanged |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | unchanged |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | unchanged |
| hermes ledger (`events.jsonl`) | `e23c5bc9` (P204 ref) | not written |

## Corpus
- vultisig src tree (`audits/vultisig-2024-06-holdout/contracts/src`, all `.sol`): `d9489e47` START==END.
- `pocs/realsrc/src` **byte-identical** to production src (`diff -rq` clean).
- `_sealed_answer_key` opened **read-only**, only after FREEZE 1 (`fa1afe1b`), for blind→awarded mapping; not modified.
- symlink quantamm active audit untouched; no other corpus modified.

## Blind firewall
- 8 prompts = production deep_trace.md + verbatim source only; token-scan **CLEAN** (no `[H-0`/`[M-0`/`[C-0`/
  `code-423n4`/severity-criteria).
- Fresh key-blind Sonnet subagents; FREEZE 1 raw-outputs hash `fa1afe1b` recorded before key open.
- Raw outputs are structured distillations (verdict + mechanisms preserved in substance); full reasoning in transcript.
- Scorer/mapping post-freeze; no backfill into blind outputs.

## Harness isolation & honesty
- All harness artifacts under `documentation/research/assisted_mode/p205_l3_vultisig_validation/pocs/` (self-contained
  foundry project, forge-std-free). No production/test code outside this dir touched.
- forge 1.5.1 / solc 0.7.6. V07_Whitelist: **2/2 PASS** (`pocs/run_log.txt`).
- Positive control: **HARNESS_INCONCLUSIVE** — documented compile-dependency obstacle (no fabricated pass).
- `fabrication_rate = 0` — every verdict is a run log or a documented source/compile obstacle.

## Decision
`L3_STANDARD_PARTIAL`. No production change. Research-only, un-wired.
