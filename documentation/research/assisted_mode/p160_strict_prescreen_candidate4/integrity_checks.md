# P160 integrity checks

| Artifact | Baseline | Post-P160 | Result |
|---|---|---|---|
| runtime sidecar `output_research/value_provenance_eval/runtime_status.jsonl` | `491da8c1…` | `491da8c1…` | **byte-identical** (H8 not_run → no sidecar row) |
| frozen corpus `documentation/evals/judge_corpus/frozen_corpus.json` | `60089ff5…` | `60089ff5…` | **byte-identical** |
| campaign ledger `output_research/option_a_campaign/ledger.jsonl` | `d4043376…` (3 rows) | (4 rows) | **append-only +1** (H8) |
| basin `src/Well.sol` | `36e6f3a5…` | unchanged | **byte-identical** (read-only audit) |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- `sandbox_check.py` on `Well.sol` → CLEAN before reading.
- No harness built → no PoC dir, no Foundry `lib/`, no mocks, no production-source edit.
- Ledger flags forced by the tool: `research_only=true`, `routing_allowed=false`, `submission_ready=false`.
- Holdout `_sealed_answer_key` NOT opened → `duplicate_status=duplicate_unknown`.
- Un-wired: `grep option_a_campaign|p160_strict run_pipeline.sh config/agent_policy.json` → empty.
- Dashboard surfaces H8 read-only as `campaign:H8-basin-well-shift-skim-sync` (track `option_a_campaign`,
  state `STATIC_FALSE_POSITIVE`) and the deep-link `/api/candidate` resolves 200 — zero dashboard code change.
