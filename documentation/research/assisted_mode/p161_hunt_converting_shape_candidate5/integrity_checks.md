# P161 integrity checks

| Artifact | Baseline | Post-P161 | Result |
|---|---|---|---|
| runtime sidecar `output_research/value_provenance_eval/runtime_status.jsonl` | `491da8c1…` | `491da8c1…` | **byte-identical** (H9 not_run → no row) |
| frozen corpus `documentation/evals/judge_corpus/frozen_corpus.json` | `60089ff5…` | `60089ff5…` | **byte-identical** |
| campaign ledger `output_research/option_a_campaign/ledger.jsonl` | `0159ef04…` (4 rows) | (5 rows) | **append-only +1** (H9) |
| hybra `RewardsDistributor.sol` | `76821df3…` | unchanged | **byte-identical** (read-only audit) |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- `sandbox_check.py` on `RewardsDistributor.sol` → CLEAN before reading.
- No harness built → no PoC dir, no Foundry `lib/`, no mocks, no production-source edit.
- Ledger flags forced by the tool: `research_only=true`, `routing_allowed=false`, `submission_ready=false`.
- Holdout/eval `_sealed_answer_key` NOT opened → `duplicate_status=duplicate_unknown`.
- Un-wired: `grep option_a_campaign|p161_hunt run_pipeline.sh config/agent_policy.json` → empty.
- Dashboard surfaces H9 read-only as `campaign:H9-hybra-rewardsdistributor-claimmany-parity`
  (track `option_a_campaign`, state `STATIC_FALSE_POSITIVE`); deep-link `/api/candidate` resolves 200 —
  zero dashboard code change.
