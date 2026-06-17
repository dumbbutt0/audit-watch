# P148 — Safety Review

## Acceptance criteria / hard constraints — all honored
- One candidate only. ✓ (velodrome `RewardsDistributor`)
- Real-contract Foundry harness only, local mocks/controls. ✓
- No production edits — real `RewardsDistributor.sol` byte-identical (11414 bytes); mocks/control in the test. ✓
- No detector / severity / submission-gate / routing edits; no prompt edits. ✓
- **Corpus + prompt baseline byte-for-byte unchanged** — velodrome item is a **runtime-only** sidecar row, not in
  `corpus.jsonl`; `integrity.prompt_corpus_unchanged: true`; live `totals` == P138 baseline; test
  `test_runtime_refuted_does_not_perturb_prompt_metrics`. ✓
- Sidecar/panel only. ✓ (no harness `.py` change needed — `runtime_refuted` already in `RUNTIME_STATUS`; the
  not-in-corpus `runtime_only` path already existed from P147)
- Ends in a negative label: **runtime_refuted** (never `runtime_confirmed`). ✓
- No severity; no submission package; no report-draft promotion. ✓
- All rows `routing_allowed=false` + `submission_ready=false` (forced; `integrity.*_all_false: true`). ✓
- Active `output/` symlink unchanged (`quantamm-2024-12-eval`); no audit switched. ✓
- Un-wired — `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty. ✓
- P130–P147 untouched. ✓

## Honesty
- `duplicate_unknown` (no local answer key); the refutation is **specific to the recipient-divergence axis**, not a
  general safety claim about velodrome.
- The candidate was a genuine same-family suspicion (blackhole-distributor ancestor), so the negative result is a
  meaningful calibration point, not a strawman.
- `requires_human_review/poc_review = false` for the refuted row — it is killed; nothing to escalate.

## Integrity / state
2 research-only artifacts changed (`runtime_status.jsonl` +1 row; the test +3) + the velodrome `pocs/p148/`
harness; no production source touched; no harness `.py` change. Full pytest 1664 passed (1661 + 3) / 2 pre-existing
deep_solidity snapshot fails / 4 skipped. Temp `lib/`/`out/` removed post-run. Writes confined to
`output_research/`, the holdout `pocs/p148/`, `tests/research/`, and the deliverables.
