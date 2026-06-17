# P159 integrity checks

All verified post-phase (read-only confirmation; nothing in the production system changed).

| Artifact | Baseline | Post-P159 | Result |
|---|---|---|---|
| runtime sidecar `output_research/value_provenance_eval/runtime_status.jsonl` | `491da8c11671b016d26f119888e39c1d` | `491da8c11671b016d26f119888e39c1d` | **byte-identical** (H7 not_run → no sidecar row) |
| frozen corpus `documentation/evals/judge_corpus/frozen_corpus.json` | `60089ff515d27c4aa0fcf96dfdea049e` | `60089ff515d27c4aa0fcf96dfdea049e` | **byte-identical** |
| campaign ledger `output_research/option_a_campaign/ledger.jsonl` | `89f4c103…` (2 rows) | `d4043376…` (3 rows) | **append-only +1** (H7) |
| Wildcat market sources (`src/market/*.sol`) | 785f7be6 / 178b294a / 24a05588 / d5429905 / 4da20c3c | unchanged | **byte-identical** (read-only audit) |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- `sandbox_check.py` run before reading untrusted source → CLEAN.
- Un-wired: `grep option_a_campaign|p159_wildcat run_pipeline.sh config/agent_policy.json` → empty.
- Ledger row flags forced by the tool: `research_only=true`, `routing_allowed=false`, `submission_ready=false`.
- Holdout `_sealed_answer_key` NOT opened → `duplicate_status=duplicate_unknown`.
- Dashboard surfaces H7 read-only (`/api/candidates` → `campaign:H7-…`, track `option_a_campaign`, state
  `STATIC_FALSE_POSITIVE`; detail deep-link resolves 200) with **zero dashboard code change**.
- No harness built → no `lib/` to remove; no Foundry artifacts created.
