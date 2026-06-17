# P150 — Safety Review

## Hard constraints — all honored
- One fresh candidate, not noya/blackhole/centrifuge/velodrome, `duplicate_unknown` (decent holdout, no answer key). ✓
- Real-contract Foundry harness; mocks for deps only; corrected reference + matched control included. ✓
- No production contract edit — real `UTBFeeCollector.sol` byte-identical (2629 bytes); mocks/control in the test. ✓
- No detector / severity / submission-gate / routing / prompt edits; no harness logic change (no `P150` ref in
  `value_provenance_eval_harness.py`). ✓
- **Corpus + prompt baseline byte-for-byte unchanged** — H3 is a sidecar **runtime-only** row, not in
  `corpus.jsonl`; `integrity.prompt_corpus_unchanged: true`; live `totals` == P138 baseline; test
  `test_decent_row_does_not_perturb_prompt_metrics`. ✓
- Sidecar/runtime-only panel row only. ✓
- All rows `routing_allowed=false` + `submission_ready=false` (forced; `integrity.*_all_false: true`). ✓
- `duplicate_status=duplicate_unknown` (no novelty inference). ✓
- Active `output/` symlink unchanged (`quantamm-2024-12-eval`); no audit switched. ✓
- Un-wired — `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty. ✓
- No submission package; not submission-ready. ✓ P130–P149 untouched. ✓

## Honesty (not biased toward confirmation)
- The classification followed the runtime result. `runtime_confirmed` is scoped to the **contract-level mechanism**
  (signature does not bind the executed fee); **reachability/severity is explicitly deferred** (onlyUtb + UTB flow
  + replay) to human review, mirroring P147/P149 discipline.
- No external docs used (local source only).

## Integrity / state
2 research-only artifacts changed (`runtime_status.jsonl` +1 row; the test +2) + the decent `pocs/p150/` harness;
no production source / harness-logic change. Full pytest 1668 passed (1666 + 2) / 2 pre-existing deep_solidity
snapshot fails / 4 skipped. Temp `lib/`/`out/` removed post-run. Writes confined to `output_research/`, the holdout
`pocs/p150/`, `tests/research/`, and the deliverables.
